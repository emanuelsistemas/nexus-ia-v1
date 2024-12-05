# Estrutura do Sistema

## 1. Sistema Base (Core)

### Backup
```
core/backup/
├── manager.py      # Gerenciador principal de backups
├── scheduler.py    # Agendador de backups automáticos
└── validator.py    # Validador de integridade
```

### Checkpoints
```
core/checkpoints/
├── manager.py      # Gerenciador de checkpoints
├── monitor.py      # Monitor de métricas
└── triggers.py     # Regras de trigger
```

### RAG (Retrieval Augmented Generation)
```
core/knowledge/
├── store.py        # Armazenamento Chroma
├── context.py      # Gerenciador de contextos
└── cache.py        # Sistema de cache
```

### Segurança
```
core/security/
├── auth.py         # Autenticação
├── crypto.py       # Criptografia
└── audit.py        # Logs de auditoria
```

## 2. Projetos
```
projects/
├── registry.py     # Registro central
└── [projeto]/      # Pasta específica por projeto
    ├── config/     # Configurações
    ├── data/       # Dados do projeto
    └── backup/     # Backups isolados
```

## 3. API
```
api/v1/
├── backup.py       # Endpoints de backup
├── projects.py     # Gestão de projetos
└── knowledge.py    # Endpoints do RAG
```

## 4. Recursos Compartilhados
```
shared/
├── models/         # Modelos de dados
├── utils/          # Utilitários
└── constants/      # Configurações
```

## Fluxo de Dados

1. **Backup**:
   ```
   Projeto -> BackupManager -> Storage -> Validação -> Logs
   ```

2. **Checkpoints**:
   ```
   Monitor -> Triggers -> CheckpointManager -> Backup -> Logs
   ```

3. **RAG**:
   ```
   Query -> Contexto -> Cache -> Chroma -> Resposta
   ```

4. **Projetos**:
   ```
   Registro -> Configuração -> Isolamento -> Execução
   ```
