#!/bin/bash

echo "=== Limpando processos existentes ==="
pkill -9 -f "python main.py" || true
pkill -9 -f "uvicorn" || true
lsof -ti:8001 | xargs kill -9 || true
sleep 2

echo "=== Iniciando servidor ==="
cd /root/project/nexus/nexus-ia/v1
source venv/bin/activate
PYTHONPATH=/root/project/nexus/nexus-ia/v1 uvicorn main:app --host 0.0.0.0 --port 8001 --reload > server.log 2>&1 &

echo "=== Aguardando servidor iniciar ==="
sleep 5

echo "=== Verificando status do servidor ==="
if pgrep -f "uvicorn" > /dev/null; then
    echo "Servidor iniciado com sucesso!"
    echo "=== Últimas 10 linhas do log ==="
    tail -n 10 server.log
    echo "\n=== Testando endpoint de saúde ==="
    curl -s http://localhost:8001/health || echo "Falha ao acessar endpoint de saúde"
else
    echo "Falha ao iniciar servidor!"
    echo "=== Log de erro ==="
    cat server.log
fi

