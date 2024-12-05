from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from core.backup.models import BackupType, BackupStatus, BackupMetadata
from core.backup.manager import BackupManager
from core.backup.logger import BackupLogger, LogLevel

router = APIRouter(prefix="/backup", tags=["backup"])

# Inicializa gerenciadores
backup_manager = BackupManager("/data/backups")
backup_logger = BackupLogger("/data/logs")

class CreateBackupRequest(BaseModel):
    project_id: str
    backup_type: BackupType
    data_dir: str
    tags: Optional[Dict[str, str]] = None
    extra: Optional[Dict[str, Any]] = None

class RestoreBackupRequest(BaseModel):
    project_id: str
    backup_id: str
    restore_dir: str

class LogFilter(BaseModel):
    project_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    level: Optional[LogLevel] = None
    backup_id: Optional[str] = None

@router.post("/create")
async def create_backup(request: CreateBackupRequest) -> BackupMetadata:
    """Cria um novo backup"""
    try:
        backup_logger.log(
            level=LogLevel.INFO,
            project_id=request.project_id,
            action="CREATE_BACKUP",
            status="STARTED",
            message=f"Iniciando backup do tipo {request.backup_type}"
        )

        metadata = backup_manager.create_backup(
            project_id=request.project_id,
            backup_type=request.backup_type,
            data_dir=request.data_dir,
            tags=request.tags,
            extra=request.extra
        )

        backup_logger.log(
            level=LogLevel.INFO,
            project_id=request.project_id,
            action="CREATE_BACKUP",
            status="COMPLETED",
            message="Backup criado com sucesso",
            backup_id=metadata.id,
            details={
                "size": metadata.size_bytes,
                "files": metadata.files_count
            }
        )

        return metadata

    except Exception as e:
        backup_logger.log(
            level=LogLevel.ERROR,
            project_id=request.project_id,
            action="CREATE_BACKUP",
            status="FAILED",
            message="Erro ao criar backup",
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
async def restore_backup(request: RestoreBackupRequest) -> bool:
    """Restaura um backup"""
    try:
        backup_logger.log(
            level=LogLevel.INFO,
            project_id=request.project_id,
            action="RESTORE_BACKUP",
            status="STARTED",
            message="Iniciando restauração",
            backup_id=request.backup_id
        )

        success = backup_manager.restore_backup(
            backup_id=request.backup_id,
            project_id=request.project_id,
            restore_dir=request.restore_dir
        )

        if success:
            backup_logger.log(
                level=LogLevel.INFO,
                project_id=request.project_id,
                action="RESTORE_BACKUP",
                status="COMPLETED",
                message="Restauração concluída",
                backup_id=request.backup_id
            )
        else:
            backup_logger.log(
                level=LogLevel.ERROR,
                project_id=request.project_id,
                action="RESTORE_BACKUP",
                status="FAILED",
                message="Falha na restauração",
                backup_id=request.backup_id
            )

        return success

    except Exception as e:
        backup_logger.log(
            level=LogLevel.ERROR,
            project_id=request.project_id,
            action="RESTORE_BACKUP",
            status="FAILED",
            message="Erro ao restaurar backup",
            backup_id=request.backup_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/{project_id}")
async def list_backups(project_id: str) -> List[BackupMetadata]:
    """Lista todos os backups de um projeto"""
    try:
        return backup_manager.list_backups(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{project_id}/{backup_id}")
async def get_backup_info(project_id: str, backup_id: str) -> BackupMetadata:
    """Obtém informações de um backup específico"""
    try:
        info = backup_manager.get_backup_info(backup_id, project_id)
        if not info:
            raise HTTPException(status_code=404, detail="Backup não encontrado")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}/{backup_id}")
async def delete_backup(project_id: str, backup_id: str) -> bool:
    """Remove um backup"""
    try:
        backup_logger.log(
            level=LogLevel.INFO,
            project_id=project_id,
            action="DELETE_BACKUP",
            status="STARTED",
            message="Iniciando remoção",
            backup_id=backup_id
        )

        success = backup_manager.delete_backup(backup_id, project_id)

        if success:
            backup_logger.log(
                level=LogLevel.INFO,
                project_id=project_id,
                action="DELETE_BACKUP",
                status="COMPLETED",
                message="Backup removido",
                backup_id=backup_id
            )
        else:
            backup_logger.log(
                level=LogLevel.WARNING,
                project_id=project_id,
                action="DELETE_BACKUP",
                status="FAILED",
                message="Backup não encontrado",
                backup_id=backup_id
            )

        return success

    except Exception as e:
        backup_logger.log(
            level=LogLevel.ERROR,
            project_id=project_id,
            action="DELETE_BACKUP",
            status="FAILED",
            message="Erro ao remover backup",
            backup_id=backup_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs")
async def get_logs(filter: LogFilter) -> List[LogEntry]:
    """Recupera logs com filtros"""
    try:
        return backup_logger.get_logs(
            project_id=filter.project_id,
            start_date=filter.start_date,
            end_date=filter.end_date,
            level=filter.level,
            backup_id=filter.backup_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

