from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from core.services.service_registry import services
import traceback

router = APIRouter()

class BackupRequest(BaseModel):
    """Requisição para criar um backup"""
    project_id: str
    source_dir: str
    description: Optional[str] = ""

class BackupResponse(BaseModel):
    """Resposta com informações do backup"""
    id: str
    project_id: str
    timestamp: datetime
    description: str
    size_bytes: int
    status: str
    error_message: Optional[str] = None

@router.post("/create", response_model=BackupResponse)
async def create_backup(request: BackupRequest):
    """Cria um novo backup"""
    try:
        print(f"Recebida requisição para criar backup do projeto {request.project_id}")
        backup_service = services.get("backup")
        if not backup_service:
            raise HTTPException(status_code=503, detail="Serviço de backup não disponível")

        backup = backup_service.manager.create_backup(
            project_id=request.project_id,
            source_dir=request.source_dir,
            description=request.description
        )

        return BackupResponse(
            id=backup.id,
            project_id=backup.project_id,
            timestamp=backup.timestamp,
            description=backup.description,
            size_bytes=backup.size_bytes,
            status=backup.status,
            error_message=backup.error_message
        )

    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/{project_id}", response_model=List[BackupResponse])
async def list_backups(project_id: str):
    """Lista todos os backups de um projeto"""
    try:
        print(f"Recebida requisição para listar backups do projeto {project_id}")
        backup_service = services.get("backup")
        if not backup_service:
            raise HTTPException(status_code=503, detail="Serviço de backup não disponível")

        backups = backup_service.manager.list_backups(project_id)
        return [
            BackupResponse(
                id=backup.id,
                project_id=backup.project_id,
                timestamp=backup.timestamp,
                description=backup.description,
                size_bytes=backup.size_bytes,
                status=backup.status,
                error_message=backup.error_message
            )
            for backup in backups
        ]

    except Exception as e:
        print(f"Erro ao listar backups: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

class RestoreRequest(BaseModel):
    """Requisição para restaurar um backup"""
    project_id: str
    backup_id: str
    target_dir: str

@router.post("/restore")
async def restore_backup(request: RestoreRequest):
    """Restaura um backup"""
    try:
        print(f"Recebida requisição para restaurar backup {request.backup_id} do projeto {request.project_id}")
        backup_service = services.get("backup")
        if not backup_service:
            raise HTTPException(status_code=503, detail="Serviço de backup não disponível")

        success = backup_service.manager.restore_backup(
            project_id=request.project_id,
            backup_id=request.backup_id,
            target_dir=request.target_dir
        )

        if not success:
            raise HTTPException(status_code=404, detail="Backup não encontrado ou erro ao restaurar")

        return {"message": "Backup restaurado com sucesso"}

    except Exception as e:
        print(f"Erro ao restaurar backup: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}/{backup_id}")
async def delete_backup(project_id: str, backup_id: str):
    """Deleta um backup"""
    try:
        print(f"Recebida requisição para deletar backup {backup_id} do projeto {project_id}")
        backup_service = services.get("backup")
        if not backup_service:
            raise HTTPException(status_code=503, detail="Serviço de backup não disponível")

        success = backup_service.manager.delete_backup(
            project_id=project_id,
            backup_id=backup_id
        )

        if not success:
            raise HTTPException(status_code=404, detail="Backup não encontrado ou erro ao deletar")

        return {"message": "Backup deletado com sucesso"}

    except Exception as e:
        print(f"Erro ao deletar backup: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

