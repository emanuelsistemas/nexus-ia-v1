from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from core.backup.models import BackupMetadata, BackupType, CompressionType
from core.backup.manager import BackupManager
import os

router = APIRouter()
manager = BackupManager("/data/backups")

class CreateBackupRequest(BaseModel):
    project_id: str
    backup_type: BackupType
    data_dir: str
    compression_type: CompressionType = CompressionType.ZLIB
    compression_level: int = 6
    tags: Optional[Dict[str, str]] = None
    extra: Optional[Dict[str, Any]] = None

class RestoreBackupRequest(BaseModel):
    project_id: str
    backup_id: str
    restore_dir: str

@router.post("/backup/create")
def create_backup(body: CreateBackupRequest) -> BackupMetadata:
    """Cria um novo backup"""
    try:
        return manager.create_backup(
            project_id=body.project_id,
            backup_type=body.backup_type,
            data_dir=body.data_dir,
            compression_type=body.compression_type,
            compression_level=body.compression_level,
            tags=body.tags,
            extra=body.extra
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/restore")
def restore_backup(body: RestoreBackupRequest) -> bool:
    """Restaura um backup"""
    try:
        return manager.restore_backup(
            backup_id=body.backup_id,
            project_id=body.project_id,
            restore_dir=body.restore_dir
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backup/list/{project_id}")
def list_backups(project_id: str) -> List[BackupMetadata]:
    """Lista todos os backups de um projeto"""
    try:
        return manager.list_backups(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backup/info/{project_id}/{backup_id}")
def get_backup_info(project_id: str, backup_id: str) -> Optional[BackupMetadata]:
    """Obtém informações de um backup específico"""
    try:
        info = manager.get_backup_info(backup_id, project_id)
        if not info:
            raise HTTPException(status_code=404, detail="Backup não encontrado")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/backup/{project_id}/{backup_id}")
def delete_backup(project_id: str, backup_id: str) -> bool:
    """Remove um backup"""
    try:
        return manager.delete_backup(backup_id, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

