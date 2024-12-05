from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, List
from pydantic import BaseModel

class BackupType(str, Enum):
    FULL = "full"          # Backup completo
    INCREMENTAL = "inc"    # Apenas mudanças
    SNAPSHOT = "snap"      # Estado atual
    CHECKPOINT = "check"   # Ponto específico

class CompressionType(str, Enum):
    NONE = "none"      # Sem compressão
    ZLIB = "zlib"      # Compressão zlib
    GZIP = "gzip"      # Compressão gzip
    LZMA = "lzma"      # Compressão LZMA (mais lenta mas melhor taxa)

class BackupStatus(str, Enum):
    PENDING = "pending"        # Iniciado
    RUNNING = "running"        # Em execução
    COMPRESSING = "compressing" # Comprimindo
    COMPLETED = "completed"    # Finalizado
    FAILED = "failed"          # Falhou
    VALIDATING = "validating"  # Validando
    RESTORING = "restoring"    # Restaurando

class CompressionInfo(BaseModel):
    """Informações sobre a compressão"""
    type: CompressionType
    original_size: int          # Tamanho original em bytes
    compressed_size: int        # Tamanho após compressão
    ratio: float               # Taxa de compressão (original/compressed)
    level: int                 # Nível de compressão usado (1-9)

class FileInfo(BaseModel):
    """Informações de um arquivo"""
    path: str                  # Caminho relativo
    size: int                  # Tamanho em bytes
    modified_at: datetime      # Última modificação
    checksum: str             # Hash do arquivo
    is_deleted: bool = False   # Se foi deletado
    compressed: bool = False   # Se está comprimido

class BackupMetadata(BaseModel):
    """Metadados do backup"""
    id: str                     # ID único
    project_id: str             # ID do projeto
    type: BackupType            # Tipo do backup
    status: BackupStatus        # Status atual
    created_at: datetime        # Data de criação
    completed_at: Optional[datetime] = None  # Data de conclusão
    size_bytes: Optional[int] = None        # Tamanho total
    checksum: Optional[str] = None         # Hash para validação
    parent_backup_id: Optional[str] = None # ID do backup pai
    files_count: Optional[int] = None      # Número de arquivos
    error_message: Optional[str] = None    # Mensagem de erro
    tags: Dict[str, str] = {}             # Tags para categorização
    extra: Dict[str, Any] = {}            # Dados extras
    files: List[FileInfo] = []            # Lista de arquivos
    compression: Optional[CompressionInfo] = None  # Info de compressão

    class Config:
        use_enum_values = True
