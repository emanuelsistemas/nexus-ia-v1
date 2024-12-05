# Sistema de Backup - Documentação Detalhada

## Estrutura de Arquivos

### 1. models.py

#### Enums
- **BackupType**:
  - FULL: Backup completo do projeto
  - INCREMENTAL: Apenas mudanças desde último backup
  - SNAPSHOT: Estado atual do projeto
  - CHECKPOINT: Ponto específico (manual/automático)

- **BackupStatus**:
  - PENDING: Backup iniciado
  - RUNNING: Em execução
  - COMPLETED: Finalizado com sucesso
  - FAILED: Falhou
  - VALIDATING: Em validação
  - RESTORING: Em restauração

#### BackupMetadata
Metadados completos do backup:
- id: ID único
- project_id: ID do projeto
- type: Tipo do backup
- status: Status atual
- created_at: Data criação
- completed_at: Data conclusão
- size_bytes: Tamanho
- checksum: Hash para validação
- parent_backup_id: ID do backup pai
- files_count: Número de arquivos
- error_message: Mensagem de erro
- tags: Categorização
- extra: Dados extras

### 2. validator.py

#### BackupValidator
Responsável pela integridade dos backups:

- **calculate_checksum**:
  - Calcula MD5 do backup
  - Processa em chunks para arquivos grandes

- **validate_backup**:
  - Verifica existência
  - Valida metadados
  - Confirma checksum

- **validate_restore_point**:
  - Valida integridade
  - Verifica dependências (backups incrementais)
  - Validação recursiva se necessário

### 3. manager.py

#### BackupManager
Gerenciador central do sistema:

- **create_backup**:
  1. Gera ID único
  2. Cria diretórios
  3. Inicializa metadados
  4. Copia dados
  5. Calcula checksum
  6. Atualiza e salva metadados

- **restore_backup**:
  1. Valida backup
  2. Verifica dependências
  3. Restaura dados
  4. Confirma restauração

- **list_backups**:
  - Lista todos backups do projeto
  - Ordenados por data

- **get_backup_info**:
  - Retorna metadados específicos

- **delete_backup**:
  - Remove backup e metadados

## Estrutura de Armazenamento

```
base_dir/
└── project_id/           # Isolamento por projeto
    └── backup_id/        # ID único por backup
        ├── metadata.json # Informações e estado
        └── data/         # Dados do backup
```

## Fluxos Principais

### 1. Criação de Backup
```
Início
  ↓
Gera ID único
  ↓
Cria diretórios
  ↓
Inicializa metadados (RUNNING)
  ↓
Copia dados
  ↓
Calcula checksum
  ↓
Atualiza metadados (COMPLETED)
  ↓
Fim
```

### 2. Restauração
```
Início
  ↓
Valida backup
  ↓
Verifica dependências
  ↓
Prepara diretório destino
  ↓
Copia dados
  ↓
Confirma restauração
  ↓
Fim
```

### 3. Validação
```
Início
  ↓
Verifica existência
  ↓
Lê metadados
  ↓
Calcula checksum atual
  ↓
Compara com original
  ↓
Verifica dependências
  ↓
Fim
```

## Tratamento de Erros

1. **Criação**:
   - Limpa diretórios em caso de erro
   - Atualiza status para FAILED
   - Registra mensagem de erro

2. **Restauração**:
   - Valida antes de iniciar
   - Limpa diretório destino se falhar
   - Retorna false e registra erro

3. **Validação**:
   - Retorna tupla (sucesso, mensagem)
   - Validação em cadeia para incrementais

## Próximos Passos

1. Implementar sistema de logs detalhado
2. Adicionar compressão de dados
3. Implementar backup incremental
4. Adicionar criptografia
5. Criar interface de administração

## Considerações de Segurança

1. **Isolamento**:
   - Dados separados por projeto
   - Validação de acesso

2. **Integridade**:
   - Checksum MD5
   - Validação antes de restaurar

3. **Recuperação**:
   - Limpeza em caso de erro
   - Backup dos metadados


## Sistema de Logs

### LogLevel
- INFO: Informações gerais
- WARNING: Avisos importantes
- ERROR: Erros no sistema
- DEBUG: Informações de debug

### LogEntry
Estrutura de cada log:
- timestamp: Data/hora
- level: Nível do log
- project_id: ID do projeto
- backup_id: ID do backup (opcional)
- action: Ação realizada
- status: Status da ação
- message: Mensagem descritiva
- details: Detalhes adicionais
- error: Mensagem de erro

### Armazenamento
- Logs separados por projeto
- Um arquivo por dia
- Formato: project_YYYY-MM-DD.log

### Funcionalidades
- Registro detalhado de operações
- Filtros por data, nível e backup
- Rastreamento de erros
- Auditoria completa

## API Endpoints

### POST /backup/create
Cria novo backup
- Request: project_id, tipo, diretório
- Response: Metadados do backup

### POST /backup/restore
Restaura backup
- Request: project_id, backup_id, diretório
- Response: Sucesso/falha

### GET /backup/list/{project_id}
Lista backups do projeto
- Response: Lista de metadados

### GET /backup/info/{project_id}/{backup_id}
Informações do backup
- Response: Metadados detalhados

### DELETE /{project_id}/{backup_id}
Remove backup
- Response: Sucesso/falha

### POST /backup/logs
Consulta logs
- Request: Filtros (data, nível, etc)
- Response: Lista de logs


## Configuração do Ambiente

### Estrutura de Diretórios
```
/data/
├── backups/     # Armazenamento dos backups
└── logs/        # Logs do sistema
```

### Variáveis de Ambiente
- ENVIRONMENT: Ambiente (development/production)
- PORT: Porta do servidor (default: 8001)
- LOG_LEVEL: Nível de log (default: info)
- BACKUP_DIR: Diretório de backups
- LOG_DIR: Diretório de logs

### Serviço Systemd
O sistema roda como um serviço systemd:
- Nome: nexus-ia.service
- Porta: 8001
- Logs: 
  - /var/log/nexus-ia.log
  - /var/log/nexus-ia.error.log

### Dependências
Principais pacotes:
- FastAPI: Framework web
- Uvicorn: Servidor ASGI
- Pydantic: Validação de dados
- Python-multipart: Upload de arquivos
- Python-jose: JWT tokens
- Passlib: Hashing de senhas
- PyYAML: Parsing YAML
- Aiofiles: IO assíncrono
- Python-dotenv: Variáveis de ambiente

