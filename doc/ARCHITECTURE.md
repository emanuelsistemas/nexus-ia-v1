# Arquitetura do Sistema

## Componentes Principais

### 1. Gerenciador de Serviços
- Controle de portas
- Monitoramento de saúde
- Sistema de retry
- Logs centralizados

### 2. RAG (Retrieval Augmented Generation)
- Chroma DB para armazenamento vetorial
- Sistema de embeddings
- Busca por similaridade
- Cache de resultados

### 3. Multi-tenancy
- Isolamento por CNPJ
- Gestão de recursos
- Limites e quotas
- Backup por tenant

### 4. Frontend
- Interface React
- Chat UI
- Dashboard
- Gestão de documentos

## Fluxo de Dados
1. Usuário envia pergunta
2. Sistema busca contexto relevante no Chroma
3. Contexto + pergunta são processados pelo Ollama
4. Resposta é retornada e armazenada

## Segurança
- Autenticação JWT
- Criptografia em repouso
- Logs de auditoria
- Backup automático
