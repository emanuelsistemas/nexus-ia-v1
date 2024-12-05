#!/bin/bash

echo "Iniciando setup do backend..."

# Navega para o diretório do backend
cd /root/project/nexus/nexus-ia/v1

# Ativa o ambiente virtual
source venv/bin/activate

# Mata qualquer processo rodando na porta 8001
echo "Limpando porta 8001..."
pkill -f "uvicorn.*main:app"

# Inicia o servidor em background
echo "Iniciando servidor FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8001 > backend.log 2>&1 &

# Aguarda 5 segundos
sleep 5

# Verifica se o processo está rodando
if pgrep -f "uvicorn.*main:app" > /dev/null
then
    echo "Servidor iniciado com sucesso!"
    echo "Backend disponível em: http://5.161.236.34:8001"
    echo "Documentação API em: http://5.161.236.34:8001/docs"
    echo "Logs disponíveis em: backend.log"
else
    echo "Erro ao iniciar o servidor. Verifique os logs em backend.log"
    exit 1
fi

