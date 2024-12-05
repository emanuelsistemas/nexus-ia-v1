#!/bin/bash

# Script de Rollback para o Nexus IA V1
# Este script gerencia o processo de rollback, incluindo código, dependências e serviços

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
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
        pip check
    fi
    
    # Verificar se os arquivos principais existem
    required_files=("main.py" "requirements.txt" ".env")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "AVISO: Arquivo $file não encontrado!"
        fi
    done
}

# Função principal de rollback
function perform_rollback() {
    local commit_hash=$1
    
    log "Iniciando processo de rollback..."
    
    # 1. Backup do estado atual
    backup_current_state
    
    # 2. Executar git reset
    log "Executando git reset para $commit_hash..."
    git reset --hard "$commit_hash"
    
    # 3. Restaurar dependências
    restore_dependencies
    
    # 4. Reiniciar serviços
    restart_services
    
    # 5. Verificar integridade
    check_integrity
    
    log "Processo de rollback concluído!"
}

# Verifica se um commit hash foi fornecido
if [ -z "$1" ]; then
    commit_hash="HEAD~1"
else
    commit_hash=$1
fi

# Executa o rollback
perform_rollback "$commit_hash"
