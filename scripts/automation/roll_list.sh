#!/bin/bash

# Configuração do fuso horário para São Paulo
export TZ="America/Sao_Paulo"

# Verifica se estamos no diretório correto
if [[ ! "$PWD" == *"/nexus-ia/v1" ]]; then
    echo "ERRO: Execute este comando na pasta v1 do projeto!"
    exit 1
fi

echo "=== Commits Disponíveis para Rollback ==="
echo "Formato: [índice] hash - data - mensagem"
echo "----------------------------------------"

# Lista os últimos 20 commits com data no formato brasileiro
git log --pretty=format:"%h - %ad - %s" --date=format:"%d/%m/%Y %H:%M:%S" -n 20 | nl -v0

echo ""
echo "----------------------------------------"
echo "Para voltar ao último commit: rollback-0"
echo "Para voltar a um commit específico: rollback-[hash]"
echo "Exemplo: rollback-abc123"
