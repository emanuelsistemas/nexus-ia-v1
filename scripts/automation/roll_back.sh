#!/bin/bash

# Configuração do fuso horário para São Paulo
export TZ="America/Sao_Paulo"

# Verifica se estamos no diretório correto
if [[ ! "$PWD" == *"/nexus-ia/v1" ]]; then
    echo "ERRO: Execute este comando na pasta v1 do projeto!"
    exit 1
fi

# Verifica se foi fornecido um argumento
if [ -z "$1" ]; then
    echo "ERRO: Especifique o hash do commit ou '0' para voltar ao último commit"
    echo "Uso: rollback-[hash] ou rollback-0"
    exit 1
fi

# Se o argumento for 0, usa HEAD~1, caso contrário usa o hash fornecido
if [ "$1" = "0" ]; then
    target="HEAD~1"
    echo "Voltando para o último commit..."
else
    target="$1"
    echo "Voltando para o commit $target..."
fi

# Executa o script de rollback
./scripts/rollback.sh "$target"
