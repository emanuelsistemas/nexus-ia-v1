from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import os
import shutil
from .models import BackupMetadata, BackupType, BackupStatus, FileInfo
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

    def _get_last_backup(self, project_id: str) -> Optional[BackupMetadata]:
        """Obtém o último backup completo do projeto"""
        backups = self.list_backups(project_id)
        for backup in backups:
            if backup.type == BackupType.FULL and backup.status == BackupStatus.COMPLETED:
                return backup
        return None

    def _copy_file(self, src: str, dest: str) -> None:
        """Copia um arquivo garantindo que o diretório de destino exista"""
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)

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

            # Obtém informações dos arquivos atuais
            current_files = self.validator.scan_directory(data_dir)

            # Se for incremental, precisa do backup anterior
            if backup_type == BackupType.INCREMENTAL:
                last_backup = self._get_last_backup(project_id)
                if not last_backup:
                    raise ValueError("Nenhum backup completo encontrado para backup incremental")
                
                metadata.parent_backup_id = last_backup.id
                last_files = {f.path: f for f in last_backup.files}

                # Identifica arquivos modificados/novos/deletados
                modified_files = []
                for path, file_info in current_files.items():
                    last_file = last_files.get(path)
                    if not last_file or last_file.checksum != file_info.checksum:
                        modified_files.append(file_info)

                # Identifica arquivos deletados
                for path, last_file in last_files.items():
                    if path not in current_files:
                        modified_files.append(FileInfo(
                            path=path,
                            size=last_file.size,
                            modified_at=datetime.now(),
                            checksum=last_file.checksum,
                            is_deleted=True
                        ))

                # Copia apenas arquivos modificados
                data_backup_dir = os.path.join(backup_dir, "data")
                for file_info in modified_files:
                    if not file_info.is_deleted:
                        src = os.path.join(data_dir, file_info.path)
                        dest = os.path.join(data_backup_dir, file_info.path)
                        self._copy_file(src, dest)

                metadata.files = modified_files

            else:  # Backup completo
                # Copia todos os arquivos
                data_backup_dir = os.path.join(backup_dir, "data")
                shutil.copytree(data_dir, data_backup_dir)
                metadata.files = list(current_files.values())

            # Atualiza metadados
            size = sum(f.size for f in metadata.files if not f.is_deleted)
            metadata.size_bytes = size
            metadata.files_count = len([f for f in metadata.files if not f.is_deleted])
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

            # Carrega metadados
            backup_dir = os.path.join(self.base_dir, project_id, backup_id)
            with open(os.path.join(backup_dir, "metadata.json"), "r") as f:
                metadata = BackupMetadata.parse_raw(f.read())

            # Se for incremental, precisa restaurar a cadeia completa
            if metadata.parent_backup_id:
                # Primeiro restaura o pai
                self.restore_backup(metadata.parent_backup_id, project_id, restore_dir)

            # Aplica as alterações deste backup
            data_dir = os.path.join(backup_dir, "data")
            for file_info in metadata.files:
                dest_path = os.path.join(restore_dir, file_info.path)
                if file_info.is_deleted:
                    # Remove arquivo se foi deletado
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                else:
                    # Copia arquivo novo/modificado
                    src_path = os.path.join(data_dir, file_info.path)
                    self._copy_file(src_path, dest_path)

            return True

        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False

    def list_backups(self, project_id: str) -> List[BackupMetadata]:
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
            # Verifica se tem backups incrementais dependentes
            backups = self.list_backups(project_id)
            for backup in backups:
                if backup.parent_backup_id == backup_id:
                    raise ValueError("Não é possível remover backup com dependentes")

            backup_dir = os.path.join(self.base_dir, project_id, backup_id)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
                return True
            return False
        except Exception as e:
            print(f"Erro ao deletar backup: {e}")
            return False

