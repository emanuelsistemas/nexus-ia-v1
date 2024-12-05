from typing import Dict, Any, Optional
import os
import traceback
from .base import BaseService
from .manager import ServiceInfo as ManagerServiceInfo
from core.backup import BackupManager

class BackupService(BaseService):
    """Serviço de gerenciamento de backups"""

    def __init__(self, base_dir: str):
        print(f"Inicializando BackupService com diretório base: {base_dir}")
        super().__init__(
            name="backup",
            description="Serviço de gerenciamento de backups",
            dependencies=[],  # Por enquanto não tem dependências
            required_ports=[]  # Não requer portas específicas
        )
        self.base_dir = base_dir
        self._manager: Optional[BackupManager] = None
        self._service_info = ManagerServiceInfo(
            name="backup",
            description="Serviço de gerenciamento de backups",
            dependencies=[],
            required_ports=[]
        )
        print("BackupService inicializado")

    @property
    def info(self) -> ManagerServiceInfo:
        """Retorna as informações do serviço"""
        return self._service_info

    async def start(self) -> bool:
        """Inicia o serviço de backup"""
        try:
            print("Iniciando serviço de backup...")
            self._manager = BackupManager(self.base_dir)
            print("Serviço de backup iniciado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao iniciar serviço de backup: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())
            return False

    async def stop(self) -> bool:
        """Para o serviço de backup"""
        try:
            print("Parando serviço de backup...")
            self._manager = None
            print("Serviço de backup parado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao parar serviço de backup: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())
            return False

    async def health_check(self) -> bool:
        """Verifica se o serviço está saudável"""
        try:
            print("Executando health check do serviço de backup...")
            if not self._manager:
                print("Health check falhou: manager não inicializado")
                return False
            # Verifica se o diretório base existe e tem permissões
            is_healthy = os.path.exists(self.base_dir) and os.access(self.base_dir, os.W_OK)
            print(f"Health check concluído. Resultado: {is_healthy}")
            return is_healthy
        except Exception as e:
            print(f"Erro durante health check: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())
            return False

    async def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do serviço"""
        print("Coletando métricas do serviço de backup...")
        metrics = {
            "total_backups": 0,
            "total_size": 0,
            "projects": 0
        }

        if not self._manager:
            print("Métricas vazias: manager não inicializado")
            return metrics

        try:
            # Lista todos os projetos
            projects = set()
            total_size = 0
            total_backups = 0

            # Itera sobre os projetos no diretório base
            base_dir = self._manager.base_dir
            print(f"Escaneando diretório base: {base_dir}")
            for project_id in os.listdir(base_dir):
                project_dir = os.path.join(base_dir, project_id)
                if not os.path.isdir(project_dir):
                    continue

                projects.add(project_id)
                backups = self._manager.list_backups(project_id)
                total_backups += len(backups)
                total_size += sum(b.size_bytes for b in backups)

            metrics.update({
                "total_backups": total_backups,
                "total_size": total_size,
                "projects": len(projects)
            })

            print(f"Métricas coletadas: {metrics}")

        except Exception as e:
            print(f"Erro ao coletar métricas: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())

        return metrics

    @property
    def manager(self) -> Optional[BackupManager]:
        """Retorna o gerenciador de backup"""
        return self._manager

