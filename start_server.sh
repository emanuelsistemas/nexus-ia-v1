#!/bin/bash

# Função para limpar processos
cleanup() {
    echo "=== Limpando processos existentes ==="
    pkill -f "uvicorn main:app"
    sleep 2
}

# Função para iniciar o servidor
start_server() {
    echo "=== Iniciando servidor ==="
    cd "$(dirname "$0")"
    source venv/bin/activate
    PYTHONUNBUFFERED=1 uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-level debug 2>&1 | tee -a server.log &
}

# Função para verificar se o servidor está rodando
wait_for_server() {
    echo "=== Aguardando servidor iniciar ==="
    sleep 5
}

# Função para testar o servidor
test_server() {
    echo "=== Verificando status do servidor ==="
    if ps aux | grep -q "[u]vicorn main:app"; then
        echo "Servidor iniciado com sucesso!"
    else
        echo "Falha ao iniciar o servidor!"
        exit 1
    fi

    echo "=== Últimas 10 linhas do log ==="
    tail -n 10 server.log

    echo "\n=== Testando endpoint de saúde ==="
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
    if [ "$response" = "200" ]; then
        echo "Endpoint de saúde OK"
    else
        echo "Falha ao acessar endpoint de saúde"
        echo "Código de resposta: $response"
        echo "\n=== Log completo ==="
        cat server.log
    fi
}

# Execução principal
cleanup
start_server
wait_for_server
test_server

