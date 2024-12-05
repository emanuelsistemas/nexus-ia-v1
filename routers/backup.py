from fastapi import APIRouter, HTTPException
from typing import List, Optional
from core.backup.models import BackupMetadata, BackupType, CompressionType
from core.services import ServiceStatus
from core.services.service_registry import service_manager, services

router = APIRouter()

@router.post("/create")
async def create_backup(
    project_id: str,
    data_dir: str,
    backup_type: BackupType = BackupType.FULL,
    compression_type: CompressionType = CompressionType.ZLIB,
    compression_level: int = 6,
    tags: Optional[dict] = None,
    extra: Optional[dict] = None
) -> BackupMetadata:
    """Cria um novo backup"""
    # Verifica se o serviço está disponível
    backup_service = services.get("backup")
    if not backup_service or not backup_service.manager:
        raise HTTPException(
            status_code=503,
            detail="Serviço de backup não disponível"
        )

    # Verifica status do serviço
    service_info = service_manager.get_service_status("backup")
    if service_info != ServiceStatus.RUNNING:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço de backup não está rodando (status: {service_info})"
        )

    try:
        return backup_service.manager.create_backup(
            project_id=project_id,
            backup_type=backup_type,
            data_dir=data_dir,
            compression_type=compression_type,
            compression_level=compression_level,
            tags=tags,
            extra=extra
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar backup: {str(e)}"
        )

@router.post("/restore")
async def restore_backup(
    project_id: str,
    backup_id: str,
    restore_dir: str
) -> bool:
    """Restaura um backup"""
    # Verifica se o serviço está disponível
    backup_service = services.get("backup")
    if not backup_service or not backup_service.manager:
        raise HTTPException(
            status_code=503,
            detail="Serviço de backup não disponível"
        )

    # Verifica status do serviço
    service_info = service_manager.get_service_status("backup")
    if service_info != ServiceStatus.RUNNING:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço de backup não está rodando (status: {service_info})"
        )

    try:
        return backup_service.manager.restore_backup(
            backup_id=backup_id,
            project_id=project_id,
            restore_dir=restore_dir
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao restaurar backup: {str(e)}"
        )

@router.get("/list/{project_id}", response_model=List[BackupMetadata])
async def list_backups(project_id: str) -> List[BackupMetadata]:
    """Lista todos os backups de um projeto"""
    # Verifica se o serviço está disponível
    backup_service = services.get("backup")
    if not backup_service or not backup_service.manager:
        raise HTTPException(
            status_code=503,
            detail="Serviço de backup não disponível"
        )

    # Verifica status do serviço
    service_info = service_manager.get_service_status("backup")
    if service_info != ServiceStatus.RUNNING:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço de backup não está rodando (status: {service_info})"
        )

    try:
        return backup_service.manager.list_backups(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar backups: {str(e)}"
        )

@router.get("/info/{project_id}/{backup_id}", response_model=Optional[BackupMetadata])
async def get_backup_info(project_id: str, backup_id: str) -> Optional[BackupMetadata]:
    """Obtém informações de um backup específico"""
    # Verifica se o serviço está disponível
    backup_service = services.get("backup")
    if not backup_service or not backup_service.manager:
        raise HTTPException(
            status_code=503,
            detail="Serviço de backup não disponível"
        )

    # Verifica status do serviço
    service_info = service_manager.get_service_status("backup")
    if service_info != ServiceStatus.RUNNING:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço de backup não está rodando (status: {service_info})"
        )

    try:
        info = backup_service.manager.get_backup_info(backup_id, project_id)
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Backup {backup_id} não encontrado"
            )
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter informações do backup: {str(e)}"
        )

@router.delete("/delete/{project_id}/{backup_id}")
async def delete_backup(project_id: str, backup_id: str) -> bool:
    """Remove um backup"""
    # Verifica se o serviço está disponível
    backup_service = services.get("backup")
    if not backup_service or not backup_service.manager:
        raise HTTPException(
            status_code=503,
            detail="Serviço de backup não disponível"
        )

    # Verifica status do serviço
    service_info = service_manager.get_service_status("backup")
    if service_info != ServiceStatus.RUNNING:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço de backup não está rodando (status: {service_info})"
        )

    try:
        if not backup_service.manager.delete_backup(backup_id, project_id):
            raise HTTPException(
                status_code=404,
                detail=f"Backup {backup_id} não encontrado"
            )
        return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar backup: {str(e)}"
        )

