#!/bin/bash

# Verifica se está no diretório correto
current_dir=$(pwd)
if [[ "$current_dir" != *"/nexus-ia/v1" ]]; then
    echo "ERRO: Você não está no diretório correto!"
    echo "Diretório atual: $current_dir"
    echo "Por favor, vá para o diretório /nexus-ia/v1 antes de executar o rollback"
    echo "Use: cd /caminho/para/nexus-ia/v1"
    exit 1
fi

echo "OK! Você está no diretório correto para executar o rollback"
echo "Para fazer rollback, use um dos comandos:"
echo "  ./scripts/rollback.sh HEAD~1          # para voltar 1 commit"
echo "  ./scripts/rollback.sh <hash>          # para voltar para um commit específico"
echo ""
echo "Commits disponíveis:"
git log --oneline -n 5
