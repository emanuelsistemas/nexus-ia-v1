import os
import hashlib
from typing import Dict, Tuple, Optional
from .models import FileInfo

class BackupValidator:
    """Validador de backups"""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def calculate_checksum(self, path: str) -> str:
        """Calcula o checksum de um arquivo ou diretório"""
        if not os.path.exists(path):
            return ""

        if os.path.isfile(path):
            # Para arquivo, calcula o hash do conteúdo
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        else:
            # Para diretório, combina os hashes dos arquivos
            hasher = hashlib.sha256()
            for root, _, files in os.walk(path):
                for file in sorted(files):  # Ordena para consistência
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)
                    hasher.update(rel_path.encode())
                    file_hash = self.calculate_checksum(file_path)
                    hasher.update(file_hash.encode())
            return hasher.hexdigest()

    def scan_directory(self, path: str) -> Dict[str, FileInfo]:
        """Escaneia um diretório e retorna informações dos arquivos"""
        files = {}
        if not os.path.exists(path):
            return files

        for root, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, path)
                stat = os.stat(file_path)
                files[rel_path] = FileInfo(
                    path=rel_path,
                    size=stat.st_size,
                    modified_at=stat.st_mtime,
                    checksum=hashlib.md5(
                        open(file_path, "rb").read()
                    ).hexdigest()
                )

        return files

    def validate_restore_point(self, backup_id: str, project_id: str) -> Tuple[bool, Optional[str]]:
        """Valida um ponto de restauração"""
        backup_dir = os.path.join(self.base_dir, project_id, backup_id)
        data_dir = os.path.join(backup_dir, "data")

        # Verifica se o diretório do backup existe
        if not os.path.exists(backup_dir):
            return False, "Backup não encontrado"

        # Verifica se o diretório de dados existe
        if not os.path.exists(data_dir):
            return False, "Dados do backup não encontrados"

        # Verifica se o arquivo de metadados existe
        metadata_path = os.path.join(backup_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            return False, "Metadados do backup não encontrados"

        # Verifica se os arquivos listados nos metadados existem
        with open(metadata_path, "r") as f:
            import json
            metadata = json.load(f)
            for file_info in metadata["files"]:
                if not file_info["is_deleted"]:
                    file_path = os.path.join(data_dir, file_info["path"])
                    if metadata["compression"]:
                        compressed_path = file_path + ".compressed"
                        if not os.path.exists(compressed_path):
                            return False, "Arquivo comprimido ausente: " + file_info["path"] + ".compressed"
                    else:
                        if not os.path.exists(file_path):
                            return False, "Arquivo ausente: " + file_info["path"]

        return True, None

