from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel

class BackupType(str, Enum):
    FULL = "full"          # Backup completo do projeto
    INCREMENTAL = "inc"    # Apenas mudanças desde último backup
    SNAPSHOT = "snap"      # Estado atual do projeto
    CHECKPOINT = "check"   # Ponto específico (manual ou automático)

class BackupStatus(str, Enum):
    PENDING = "pending"    # Backup iniciado
    RUNNING = "running"    # Em execução
    COMPLETED = "completed" # Finalizado com sucesso
    FAILED = "failed"      # Falhou
    VALIDATING = "validating" # Em validação
    RESTORING = "restoring"  # Em restauração

class BackupMetadata(BaseModel):
    """Metadados do backup"""
    id: str                     # ID único do backup
    project_id: str             # ID do projeto
    type: BackupType            # Tipo do backup
    status: BackupStatus        # Status atual
    created_at: datetime        # Data de criação
    completed_at: Optional[datetime] = None  # Data de conclusão
    size_bytes: Optional[int] = None        # Tamanho em bytes
    checksum: Optional[str] = None         # Hash para validação
    parent_backup_id: Optional[str] = None # ID do backup pai (para incremental)
    files_count: Optional[int] = None      # Número de arquivos
    error_message: Optional[str] = None    # Mensagem de erro se falhou
    tags: Dict[str, str] = {}             # Tags para categorização
    extra: Dict[str, Any] = {}            # Dados extras específicos do projeto

    class Config:
        use_enum_values = True
