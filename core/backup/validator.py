from typing import Optional, Tuple, Dict
from datetime import datetime
import hashlib
import json
import os
from .models import FileInfo

class BackupValidator:
    """Validador de integridade dos backups"""

    def __init__(self, backup_dir: str):
        self.backup_dir = backup_dir

    def calculate_file_checksum(self, file_path: str) -> str:
        """Calcula o checksum de um arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_file_info(self, file_path: str, base_path: str) -> FileInfo:
        """Obtém informações de um arquivo"""
        rel_path = os.path.relpath(file_path, base_path)
        stat = os.stat(file_path)
        return FileInfo(
            path=rel_path,
            size=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            checksum=self.calculate_file_checksum(file_path)
        )

    def scan_directory(self, dir_path: str) -> Dict[str, FileInfo]:
        """Escaneia um diretório e retorna informações dos arquivos"""
        files_info = {}
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_info = self.get_file_info(file_path, dir_path)
                files_info[file_info.path] = file_info
        return files_info

    def calculate_checksum(self, dir_path: str) -> str:
        """Calcula o checksum de um diretório"""
        sha256_hash = hashlib.sha256()

        # Lista todos os arquivos e ordena para consistência
        all_files = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, dir_path)
                all_files.append((rel_path, file_path))

        # Processa arquivos em ordem
        for rel_path, file_path in sorted(all_files):
            # Adiciona o caminho relativo ao hash
            sha256_hash.update(rel_path.encode())
            
            # Adiciona o conteúdo do arquivo
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

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

            # Verifica arquivos individuais
            current_files = self.scan_directory(data_path)
            for file_info in metadata.get("files", []):
                if file_info["is_deleted"]:
                    continue

                current_file = current_files.get(file_info["path"])
                if not current_file:
                    return False, f"Arquivo ausente: {file_info["path"]}"

                if current_file.checksum != file_info["checksum"]:
                    return False, f"Checksum inválido para: {file_info["path"]}"

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

