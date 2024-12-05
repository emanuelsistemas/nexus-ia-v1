# Sistema de Backup - Documentação Técnica

## Visão Geral

O sistema de backup é um componente crucial do Nexus IA, responsável por gerenciar backups de projetos de forma segura e eficiente. Ele oferece funcionalidades completas de backup, incluindo criação, restauração, listagem e gerenciamento de metadados.

## Arquitetura

O sistema é composto por quatro componentes principais:

1. **Models (models.py)**
   - Define as estruturas de dados usando Pydantic
   - Inclui enums para tipos e status de backup
   - Gerencia metadados dos backups

2. **Validator (validator.py)**
   - Valida integridade dos backups
   - Calcula e verifica checksums
   - Valida pontos de restauração

3. **Manager (manager.py)**
   - Gerencia operações de backup
   - Coordena criação e restauração
   - Mantém metadados atualizados

4. **Logger (logger.py)**
   - Registra todas as operações
   - Mantém histórico de ações
   - Facilita diagnóstico de problemas

## API Endpoints

### 1. Criar Backup
```http
POST /api/v1/backup/create
{
    "project_id": "string",
    "backup_type": "full",
    "data_dir": "string",
    "tags": {"key": "value"},
    "extra": {"key": "value"}
}
```

### 2. Restaurar Backup
```http
POST /api/v1/backup/restore
{
    "project_id": "string",
    "backup_id": "string",
    "restore_dir": "string"
}
```

### 3. Listar Backups
```http
GET /api/v1/backup/list/{project_id}
```

### 4. Obter Informações
```http
GET /api/v1/backup/info/{project_id}/{backup_id}
```

### 5. Remover Backup
```http
DELETE /api/v1/backup/{project_id}/{backup_id}
```

## Tipos de Backup

- **FULL**: Backup completo do projeto
- **INCREMENTAL**: Apenas mudanças desde último backup
- **SNAPSHOT**: Estado atual do projeto
- **CHECKPOINT**: Ponto específico (manual ou automático)

## Status de Backup

- **PENDING**: Backup iniciado
- **RUNNING**: Em execução
- **COMPLETED**: Finalizado com sucesso
- **FAILED**: Falhou
- **VALIDATING**: Em validação
- **RESTORING**: Em restauração

## Estrutura de Armazenamento

```
/data/backups/
  ├── {project_id}/
  │   ├── backup_{id}/
  │   │   ├── data/
  │   │   └── metadata.json
  │   └── ...
  └── ...
```

## Metadados do Backup

```json
{
    "id": "string",
    "project_id": "string",
    "type": "string",
    "status": "string",
    "created_at": "datetime",
    "completed_at": "datetime",
    "size_bytes": "integer",
    "checksum": "string",
    "parent_backup_id": "string",
    "files_count": "integer",
    "error_message": "string",
    "tags": {},
    "extra": {}
}
```

## Sistema de Logs

Os logs são armazenados em `/data/logs/` com o formato:
`{project_id}_{YYYY-MM-DD}.log`

### Níveis de Log
- INFO: Informações gerais
- WARNING: Avisos importantes
- ERROR: Erros críticos
- DEBUG: Informações de debug

## Testes Realizados

1. ✅ Criação de backup
   - Criado backup de teste
   - Verificado metadados
   - Confirmado checksum

2. ✅ Listagem de backups
   - Listagem correta
   - Ordenação por data
   - Filtros funcionando

3. ✅ Restauração
   - Restauração bem-sucedida
   - Integridade verificada
   - Conteúdo correto

4. ✅ Informações detalhadas
   - Todos metadados presentes
   - Informações precisas

5. ✅ Remoção
   - Remoção bem-sucedida
   - Verificação pós-remoção

## Considerações de Segurança

1. Validação de integridade via checksums
2. Logs detalhados de todas operações
3. Validação de restauração antes de executar
4. Limpeza automática em caso de falha

## Boas Práticas

1. Sempre use tipos de backup apropriados
2. Mantenha tags organizadas
3. Monitore logs regularmente
4. Valide backups periodicamente
5. Mantenha documentação atualizada

## Próximos Passos

1. Implementar backup incremental
2. Adicionar compressão
3. Implementar retenção automática
4. Adicionar métricas de performance
5. Implementar backup distribuído

