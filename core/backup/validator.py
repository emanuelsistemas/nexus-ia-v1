from typing import Optional, Tuple
from datetime import datetime
import hashlib
import json
import os

class BackupValidator:
    """Validador de integridade dos backups"""

    def __init__(self, backup_dir: str):
        self.backup_dir = backup_dir

    def calculate_checksum(self, file_path: str) -> str:
        """Calcula o checksum de um arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def validate_backup(self, backup_id: str, project_id: str) -> Tuple[bool, Optional[str]]:
        """Valida a integridade de um backup"""
        try:
            # Caminho do backup
            backup_path = os.path.join(self.backup_dir, project_id, backup_id)
            
            # Verifica se existe
            if not os.path.exists(backup_path):
                return False, "Backup não encontrado"

            # Lê metadados
            meta_path = os.path.join(backup_path, "metadata.json")
            if not os.path.exists(meta_path):
                return False, "Metadados não encontrados"

            with open(meta_path, "r") as f:
                metadata = json.load(f)

            # Verifica checksum
            data_path = os.path.join(backup_path, "data")
            current_checksum = self.calculate_checksum(data_path)

            if current_checksum != metadata.get("checksum"):
                return False, "Checksum inválido"

            return True, None

        except Exception as e:
            return False, str(e)

    def validate_restore_point(self, backup_id: str, project_id: str) -> Tuple[bool, Optional[str]]:
        """Valida se um backup pode ser restaurado"""
        # Primeiro valida integridade
        is_valid, error = self.validate_backup(backup_id, project_id)
        if not is_valid:
            return False, error

        try:
            # Verifica dependências (para backups incrementais)
            meta_path = os.path.join(self.backup_dir, project_id, backup_id, "metadata.json")
            with open(meta_path, "r") as f:
                metadata = json.load(f)

            parent_id = metadata.get("parent_backup_id")
            if parent_id:
                # Valida backup pai recursivamente
                return self.validate_restore_point(parent_id, project_id)

            return True, None

        except Exception as e:
            return False, str(e)

