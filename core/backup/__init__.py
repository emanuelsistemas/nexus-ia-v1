from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import os
import json
import shutil
import traceback

@dataclass
class BackupInfo:
    """Informações sobre um backup"""
    id: str
    project_id: str
    timestamp: datetime
    description: str
    size_bytes: int
    status: str  # success, failed, in_progress
    error_message: Optional[str] = None

class BackupManager:
    """Gerenciador de backups"""

    def __init__(self, base_dir: str):
        print(f"Inicializando BackupManager com diretório base: {base_dir}")
        self.base_dir = base_dir
        self._ensure_directories()
        print("BackupManager inicializado com sucesso")

    def _ensure_directories(self):
        """Garante que os diretórios necessários existem"""
        try:
            print("Verificando diretórios...")
            os.makedirs(self.base_dir, exist_ok=True)
            print(f"Diretório base criado/verificado: {self.base_dir}")
        except Exception as e:
            print(f"Erro ao criar diretórios: {e}")
            print(traceback.format_exc())
            raise

    def _get_project_dir(self, project_id: str) -> str:
        """Retorna o diretório de um projeto"""
        return os.path.join(self.base_dir, project_id)

    def _get_backup_dir(self, project_id: str, backup_id: str) -> str:
        """Retorna o diretório de um backup específico"""
        return os.path.join(self._get_project_dir(project_id), backup_id)

    def _get_backup_info_path(self, project_id: str, backup_id: str) -> str:
        """Retorna o caminho do arquivo de informações do backup"""
        return os.path.join(self._get_backup_dir(project_id, backup_id), "info.json")

    def _save_backup_info(self, backup: BackupInfo):
        """Salva as informações do backup"""
        try:
            print(f"Salvando informações do backup {backup.id}")
            info_path = self._get_backup_info_path(backup.project_id, backup.id)
            info_dict = {
                "id": backup.id,
                "project_id": backup.project_id,
                "timestamp": backup.timestamp.isoformat(),
                "description": backup.description,
                "size_bytes": backup.size_bytes,
                "status": backup.status,
                "error_message": backup.error_message
            }
            os.makedirs(os.path.dirname(info_path), exist_ok=True)
            with open(info_path, "w") as f:
                json.dump(info_dict, f, indent=2)
            print(f"Informações do backup {backup.id} salvas com sucesso")
        except Exception as e:
            print(f"Erro ao salvar informações do backup: {e}")
            print(traceback.format_exc())
            raise

    def _load_backup_info(self, project_id: str, backup_id: str) -> Optional[BackupInfo]:
        """Carrega as informações de um backup"""
        try:
            print(f"Carregando informações do backup {backup_id}")
            info_path = self._get_backup_info_path(project_id, backup_id)
            if not os.path.exists(info_path):
                print(f"Arquivo de informações não encontrado: {info_path}")
                return None

            with open(info_path, "r") as f:
                info_dict = json.load(f)

            backup = BackupInfo(
                id=info_dict["id"],
                project_id=info_dict["project_id"],
                timestamp=datetime.fromisoformat(info_dict["timestamp"]),
                description=info_dict["description"],
                size_bytes=info_dict["size_bytes"],
                status=info_dict["status"],
                error_message=info_dict.get("error_message")
            )
            print(f"Informações do backup {backup_id} carregadas com sucesso")
            return backup
        except Exception as e:
            print(f"Erro ao carregar informações do backup: {e}")
            print(traceback.format_exc())
            return None

    def create_backup(self, project_id: str, source_dir: str, description: str = "") -> BackupInfo:
        """Cria um novo backup"""
        try:
            print(f"Iniciando backup do projeto {project_id}")
            # Gera ID único para o backup usando timestamp
            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self._get_backup_dir(project_id, backup_id)

            # Cria o backup com status inicial
            backup = BackupInfo(
                id=backup_id,
                project_id=project_id,
                timestamp=datetime.now(),
                description=description,
                size_bytes=0,
                status="in_progress"
            )
            self._save_backup_info(backup)

            try:
                # Copia os arquivos
                print(f"Copiando arquivos de {source_dir} para {backup_dir}")
                shutil.copytree(source_dir, backup_dir)

                # Atualiza o tamanho e status
                total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                for dirpath, _, filenames in os.walk(backup_dir)
                                for filename in filenames)

                backup.size_bytes = total_size
                backup.status = "success"
                print(f"Backup {backup_id} criado com sucesso. Tamanho: {total_size} bytes")

            except Exception as e:
                backup.status = "failed"
                backup.error_message = str(e)
                print(f"Erro ao criar backup: {e}")
                print(traceback.format_exc())

            self._save_backup_info(backup)
            return backup

        except Exception as e:
            print(f"Erro crítico ao criar backup: {e}")
            print(traceback.format_exc())
            raise

    def list_backups(self, project_id: str) -> List[BackupInfo]:
        """Lista todos os backups de um projeto"""
        try:
            print(f"Listando backups do projeto {project_id}")
            project_dir = self._get_project_dir(project_id)
            if not os.path.exists(project_dir):
                print(f"Diretório do projeto não encontrado: {project_dir}")
                return []

            backups = []
            for backup_id in os.listdir(project_dir):
                backup = self._load_backup_info(project_id, backup_id)
                if backup:
                    backups.append(backup)

            # Ordena por timestamp, mais recente primeiro
            backups.sort(key=lambda x: x.timestamp, reverse=True)
            print(f"Encontrados {len(backups)} backups para o projeto {project_id}")
            return backups

        except Exception as e:
            print(f"Erro ao listar backups: {e}")
            print(traceback.format_exc())
            return []

    def restore_backup(self, project_id: str, backup_id: str, target_dir: str) -> bool:
        """Restaura um backup"""
        try:
            print(f"Iniciando restauração do backup {backup_id} do projeto {project_id}")
            backup_dir = self._get_backup_dir(project_id, backup_id)
            if not os.path.exists(backup_dir):
                print(f"Diretório do backup não encontrado: {backup_dir}")
                return False

            # Remove o diretório de destino se existir
            if os.path.exists(target_dir):
                print(f"Removendo diretório de destino existente: {target_dir}")
                shutil.rmtree(target_dir)

            # Copia os arquivos do backup
            print(f"Copiando arquivos de {backup_dir} para {target_dir}")
            shutil.copytree(backup_dir, target_dir)
            print(f"Backup {backup_id} restaurado com sucesso")
            return True

        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            print(traceback.format_exc())
            return False

    def delete_backup(self, project_id: str, backup_id: str) -> bool:
        """Deleta um backup"""
        try:
            print(f"Iniciando deleção do backup {backup_id} do projeto {project_id}")
            backup_dir = self._get_backup_dir(project_id, backup_id)
            if not os.path.exists(backup_dir):
                print(f"Diretório do backup não encontrado: {backup_dir}")
                return False

            # Remove o diretório do backup
            shutil.rmtree(backup_dir)
            print(f"Backup {backup_id} deletado com sucesso")
            return True

        except Exception as e:
            print(f"Erro ao deletar backup: {e}")
            print(traceback.format_exc())
            return False

