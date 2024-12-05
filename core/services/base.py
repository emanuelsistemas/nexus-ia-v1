from typing import List, Optional
from dataclasses import dataclass
import traceback

@dataclass
class ServiceInfo:
    """Informações sobre um serviço"""
    name: str
    description: str
    dependencies: List[str]
    required_ports: List[int]

class BaseService:
    """Classe base para todos os serviços"""

    def __init__(self, name: str, description: str, dependencies: Optional[List[str]] = None, required_ports: Optional[List[int]] = None):
        print(f"Inicializando serviço base: {name}")
        self._service_info = ServiceInfo(
            name=name,
            description=description,
            dependencies=dependencies or [],
            required_ports=required_ports or []
        )
        print(f"Serviço base {name} inicializado com sucesso")

    @property
    def info(self) -> ServiceInfo:
        """Retorna as informações do serviço"""
        return self._service_info

    async def start(self) -> bool:
        """Inicia o serviço"""
        try:
            print(f"Iniciando serviço {self.info.name}...")
            # Implementação padrão - deve ser sobrescrita
            print(f"Serviço {self.info.name} iniciado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao iniciar serviço {self.info.name}: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())
            return False

    async def stop(self) -> bool:
        """Para o serviço"""
        try:
            print(f"Parando serviço {self.info.name}...")
            # Implementação padrão - deve ser sobrescrita
            print(f"Serviço {self.info.name} parado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao parar serviço {self.info.name}: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())
            return False

    async def health_check(self) -> bool:
        """Verifica se o serviço está saudável"""
        try:
            print(f"Executando health check do serviço {self.info.name}...")
            # Implementação padrão - deve ser sobrescrita
            print(f"Health check do serviço {self.info.name} concluído com sucesso")
            return True
        except Exception as e:
            print(f"Erro durante health check do serviço {self.info.name}: {e}")
            print("Stacktrace:")
            print(traceback.format_exc())
            return False

