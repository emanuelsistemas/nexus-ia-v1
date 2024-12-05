#!/bin/bash

echo "=== Iniciando setup do frontend ==="

# Diretório do frontend
FRONTEND_DIR="/root/project/nexus/nexus-ia/v1/frontend"

# Mata processos existentes
echo "Matando processos existentes..."
pkill -f "node" || true
pkill -f "vite" || true
pkill -f "http-server" || true

# Limpa a porta 3000
fuser -k 3000/tcp || true

# Navega para o diretório
cd "$FRONTEND_DIR"

# Instala dependências
echo "Instalando dependências..."
npm install

# Faz o build
echo "Fazendo build do projeto..."
npm run build

# Inicia o servidor
echo "Iniciando servidor..."
cd dist && http-server -p 3000 --cors

