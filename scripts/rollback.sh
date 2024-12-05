#!/bin/bash

# Script de Rollback para o Nexus IA V1
# Este script gerencia o processo de rollback, incluindo código, dependências e serviços

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

function cleanup_backups() {
    log "Limpando arquivos de backup..."
    if [ -f .backup_requirements.txt ]; then
        rm .backup_requirements.txt
        log "Arquivo .backup_requirements.txt removido"
    fi
    if [ -f .env.backup ]; then
        rm .env.backup
        log "Arquivo .env.backup removido"
    fi
    # Remove qualquer outro arquivo de backup temporário
    find . -name "*.backup" -type f -delete
    find . -name "*.bak" -type f -delete
}

function backup_current_state() {
    log "Fazendo backup do estado atual..."
    # Backup das dependências atuais
    pip freeze > .backup_requirements.txt
    # Backup de configurações
    if [ -f .env ]; then
        cp .env .env.backup
    fi
}

function restore_dependencies() {
    log "Restaurando dependências..."
    # Lê o arquivo dependencies.lock do commit atual
    if [ -f dependencies.lock ]; then
        while IFS== read -r package version hash date
        do
            if [[ ! $package =~ ^#.* ]]; then
                log "Instalando $package versão $version"
                pip install "$package==$version"
            fi
        done < dependencies.lock
    else
        log "AVISO: dependencies.lock não encontrado!"
        if [ -f requirements.txt ]; then
            log "Usando requirements.txt como fallback"
            pip install -r requirements.txt
        fi
    fi
}

function restart_services() {
    log "Reiniciando serviços..."
    # Adicione aqui os comandos para reiniciar seus serviços
    if [ -f main.py ]; then
        log "Reiniciando servidor principal..."
        # Adicione seu comando de reinício aqui
        # Exemplo: systemctl restart nexus-ia
    fi
}

function check_integrity() {
    log "Verificando integridade do sistema..."
    # Verificar se todas as dependências estão instaladas
    if [ -f requirements.txt ]; then
        if ! pip check; then
            log "ERRO: Verificação de dependências falhou!"
            return 1
        fi
    fi
    
    # Verificar se os arquivos principais existem
    required_files=("main.py" "requirements.txt" ".env")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "AVISO: Arquivo $file não encontrado!"
        fi
    done
    
    return 0
}

# Função principal de rollback
function perform_rollback() {
    local commit_hash=$1
    local rollback_success=true
    
    log "Iniciando processo de rollback..."
    
    # 1. Backup do estado atual
    backup_current_state
    
    # 2. Executar git reset
    log "Executando git reset para $commit_hash..."
    if ! git reset --hard "$commit_hash"; then
        log "ERRO: Falha ao executar git reset"
        rollback_success=false
    fi
    
    # 3. Restaurar dependências
    if [ "$rollback_success" = true ]; then
        if ! restore_dependencies; then
            log "ERRO: Falha ao restaurar dependências"
            rollback_success=false
        fi
    fi
    
    # 4. Reiniciar serviços
    if [ "$rollback_success" = true ]; then
        if ! restart_services; then
            log "ERRO: Falha ao reiniciar serviços"
            rollback_success=false
        fi
    fi
    
    # 5. Verificar integridade
    if [ "$rollback_success" = true ]; then
        if ! check_integrity; then
            log "ERRO: Verificação de integridade falhou"
            rollback_success=false
        fi
    fi
    
    # 6. Limpar ou manter backups baseado no resultado
    if [ "$rollback_success" = true ]; then
        log "Rollback concluído com sucesso!"
        cleanup_backups
    else
        log "ERRO: Rollback falhou! Mantendo arquivos de backup para possível recuperação"
        log "Arquivos de backup disponíveis em:"
        log "- .backup_requirements.txt (se existir)"
        log "- .env.backup (se existir)"
    fi
    
    return $rollback_success
}

# Verifica se um commit hash foi fornecido
if [ -z "$1" ]; then
    commit_hash="HEAD~1"
else
    commit_hash=$1
fi

# Executa o rollback
perform_rollback "$commit_hash"
