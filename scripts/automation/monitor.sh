#!/bin/bash

# Configuração do fuso horário para São Paulo
export TZ="America/Sao_Paulo"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para exibir mensagens com timestamp
log_message() {
    echo -e "${2:-$NC}[$(date '+%d/%m/%Y %H:%M:%S')] $1${NC}"
}

# Função para verificar se estamos em um repositório git
check_git_repo() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        log_message "ERRO: Este diretório não é um repositório Git!" "$RED"
        exit 1
    fi
}

# Verifica se estamos no diretório correto
if [[ ! "$PWD" == *"/nexus-ia/v1" ]]; then
    log_message "ERRO: Execute este comando na pasta v1 do projeto!" "$RED"
    exit 1
fi

# Verifica se é um repositório git
check_git_repo

# Função para fazer commit e push das alterações
commit_changes() {
    # Verifica se há alterações para commit
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_message "Preparando para commit..." "$YELLOW"
        
        # Obtém a data e hora atual
        current_datetime=$(date "+%d/%m/%Y %H:%M:%S")
        
        # Tenta fazer o commit
        if git add . && git commit -m "feat: Atualização automática - $current_datetime"; then
            log_message "Commit realizado com sucesso!" "$GREEN"
            
            # Tenta fazer o push
            if git push origin HEAD; then
                log_message "Push realizado com sucesso!" "$GREEN"
                log_message "Data e hora: $current_datetime" "$GREEN"
                return 0
            else
                log_message "ERRO: Falha ao fazer push. Tentando git pull primeiro..." "$YELLOW"
                
                # Tenta resolver conflitos com pull
                if git pull --rebase origin HEAD; then
                    log_message "Pull realizado com sucesso, tentando push novamente..." "$YELLOW"
                    if git push origin HEAD; then
                        log_message "Push realizado com sucesso após pull!" "$GREEN"
                        return 0
                    fi
                fi
                
                log_message "ERRO: Falha ao fazer push mesmo após pull" "$RED"
                return 1
            fi
        else
            log_message "ERRO: Falha ao fazer commit" "$RED"
            return 1
        fi
    else
        return 0
    fi
}

# Função para limpar e sair
cleanup() {
    log_message "Encerrando monitoramento..." "$YELLOW"
    exit 0
}

# Captura Ctrl+C
trap cleanup SIGINT SIGTERM

# Inicializa
log_message "Iniciando monitoramento de alterações..." "$GREEN"
log_message "Pressione Ctrl+C para parar" "$YELLOW"

# Mostra status inicial
log_message "Status atual do repositório:" "$YELLOW"
git status

# Loop principal com verificação manual
while true; do
    # Verifica alterações
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_message "Alterações detectadas!" "$YELLOW"
        commit_changes
    fi
    
    # Espera 10 segundos antes da próxima verificação
    sleep 10
done
