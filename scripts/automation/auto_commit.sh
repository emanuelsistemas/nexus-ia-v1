#!/bin/bash

# Configuração do fuso horário para São Paulo
export TZ="America/Sao_Paulo"

# Obtém a data e hora atual no formato brasileiro
current_datetime=$(date "+%d/%m/%Y %H:%M:%S")

# Verifica se estamos no diretório correto
if [[ ! "$PWD" == *"/nexus-ia/v1" ]]; then
    echo "ERRO: Execute este comando na pasta v1 do projeto!"
    exit 1
fi

# Adiciona todas as alterações
git add .

# Obtém o status do git para ver se há alterações
git_status=$(git status --porcelain)

if [ -z "$git_status" ]; then
    echo "Nenhuma alteração para commitar!"
    exit 0
fi

# Cria a mensagem do commit com a data
commit_message="feat: Atualização automática - $current_datetime"

# Faz o commit
if git commit -m "$commit_message"; then
    echo "Commit realizado com sucesso!"
    
    # Faz o push
    if git push origin main; then
        echo "Push realizado com sucesso!"
        echo "Data e hora do commit: $current_datetime"
    else
        echo "ERRO: Falha ao fazer push!"
        exit 1
    fi
else
    echo "ERRO: Falha ao fazer commit!"
    exit 1
fi
