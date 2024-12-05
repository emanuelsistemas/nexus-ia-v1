#!/bin/bash

echo "Iniciando setup do frontend..."

# Navega para o diretório do frontend
cd /root/project/nexus/nexus-ia/v1/frontend

# Instala as dependências
echo "Instalando dependências..."
npm install

# Mata qualquer processo rodando na porta 3000
echo "Limpando porta 3000..."
pkill -f "node.*vite"

# Inicia o servidor em background
echo "Iniciando servidor Vite..."
npm run dev > frontend.log 2>&1 &

# Aguarda 5 segundos
sleep 5

# Verifica se o processo está rodando
if pgrep -f "node.*vite" > /dev/null
then
    echo "Servidor iniciado com sucesso!"
    echo "Frontend disponível em: http://5.161.236.34:3000"
    echo "Logs disponíveis em: frontend.log"
else
    echo "Erro ao iniciar o servidor. Verifique os logs em frontend.log"
    exit 1
fi

