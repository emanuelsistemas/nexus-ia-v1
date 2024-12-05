# Arquitetura do Sistema

## 1. Core

### Backup System
- BackupManager: Gerencia backups por projeto
- BackupValidator: Valida integridade
- BackupScheduler: Agenda backups automáticos

### Checkpoint System
- CheckpointManager: Gerencia checkpoints
- MetricsCollector: Coleta métricas
- TriggerEvaluator: Avalia condições

### Recovery System
- RecoveryManager: Gerencia recuperação
- HealthMonitor: Monitora saúde
- RollbackManager: Gerencia rollbacks

### Knowledge System
- KnowledgeStore: RAG central
- ContextManager: Gerencia contextos
- CacheManager: Gerencia cache

## 2. Shared Resources

### Models
- Data models compartilhados
- Interfaces comuns
- Types e enums

### Utils
- Funções utilitárias
- Helpers comuns
- Validadores

### Constants
- Configurações
- Constantes
- Defaults

## 3. Project Management

### Registry
- ProjectRegistry: Registro de projetos
- ConfigManager: Configurações
- ResourceManager: Recursos

### Isolation
- DataIsolation: Isolamento de dados
- BackupIsolation: Isolamento de backups
- MetricsIsolation: Isolamento de métricas

## 4. API Layer

### V1
- Endpoints públicos
- Validação
- Rate limiting

### Gateway
- Roteamento
- Load balancing
- Caching
