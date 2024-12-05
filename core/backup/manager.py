from datetime import datetime
from typing import Optional, Dict, Any
import json
import os
import shutil
from .models import BackupMetadata, BackupType, BackupStatus
from .validator import BackupValidator

class BackupManager:
    """Gerenciador principal de backups"""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.validator = BackupValidator(base_dir)

    def _ensure_project_dir(self, project_id: str) -> str:
        """Garante que o diretório do projeto existe"""
        project_dir = os.path.join(self.base_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    def _generate_backup_id(self, project_id: str) -> str:
        """Gera ID único para o backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{project_id}_{timestamp}"

    def create_backup(self, 
                     project_id: str,
                     backup_type: BackupType,
                     data_dir: str,
                     tags: Optional[Dict[str, str]] = None,
                     extra: Optional[Dict[str, Any]] = None) -> BackupMetadata:
        """Cria um novo backup"""
        try:
            # Prepara diretórios
            project_dir = self._ensure_project_dir(project_id)
            backup_id = self._generate_backup_id(project_id)
            backup_dir = os.path.join(project_dir, backup_id)
            os.makedirs(backup_dir)

            # Cria metadados iniciais
            metadata = BackupMetadata(
                id=backup_id,
                project_id=project_id,
                type=backup_type,
                status=BackupStatus.RUNNING,
                created_at=datetime.now(),
                tags=tags or {},
                extra=extra or {}
            )

            # Copia dados
            data_backup_dir = os.path.join(backup_dir, "data")
            shutil.copytree(data_dir, data_backup_dir)

            # Atualiza metadados
            metadata.size_bytes = sum(os.path.getsize(os.path.join(dirpath,filename))
                for dirpath, dirnames, filenames in os.walk(data_backup_dir)
                for filename in filenames)
            
            metadata.files_count = sum(len(files) 
                for _, _, files in os.walk(data_backup_dir))

            metadata.checksum = self.validator.calculate_checksum(data_backup_dir)
            metadata.status = BackupStatus.COMPLETED
            metadata.completed_at = datetime.now()

            # Salva metadados
            with open(os.path.join(backup_dir, "metadata.json"), "w") as f:
                f.write(metadata.json())

            return metadata

        except Exception as e:
            # Em caso de erro, limpa diretório e atualiza status
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            metadata.status = BackupStatus.FAILED
            metadata.error_message = str(e)
            raise

    def restore_backup(self, backup_id: str, project_id: str, restore_dir: str) -> bool:
        """Restaura um backup"""
        try:
            # Valida backup
            is_valid, error = self.validator.validate_restore_point(backup_id, project_id)
            if not is_valid:
                raise ValueError(f"Backup inválido: {error}")

            # Prepara restauração
            backup_dir = os.path.join(self.base_dir, project_id, backup_id)
            data_dir = os.path.join(backup_dir, "data")

            # Restaura dados
            if os.path.exists(restore_dir):
                shutil.rmtree(restore_dir)
            shutil.copytree(data_dir, restore_dir)

            return True

        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False

    def list_backups(self, project_id: str) -> list[BackupMetadata]:
        """Lista todos os backups de um projeto"""
        project_dir = os.path.join(self.base_dir, project_id)
        if not os.path.exists(project_dir):
            return []

        backups = []
        for backup_id in os.listdir(project_dir):
            meta_path = os.path.join(project_dir, backup_id, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r") as f:
                    metadata = BackupMetadata.parse_raw(f.read())
                    backups.append(metadata)

        return sorted(backups, key=lambda x: x.created_at, reverse=True)

    def get_backup_info(self, backup_id: str, project_id: str) -> Optional[BackupMetadata]:
        """Obtém informações de um backup específico"""
        meta_path = os.path.join(self.base_dir, project_id, backup_id, "metadata.json")
        if not os.path.exists(meta_path):
            return None

        with open(meta_path, "r") as f:
            return BackupMetadata.parse_raw(f.read())

    def delete_backup(self, backup_id: str, project_id: str) -> bool:
        """Remove um backup"""
        try:
            backup_dir = os.path.join(self.base_dir, project_id, backup_id)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
                return True
            return False
        except Exception as e:
            print(f"Erro ao deletar backup: {e}")
            return False

