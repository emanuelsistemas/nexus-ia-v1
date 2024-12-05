from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime
import threading
import time
import traceback

class ServiceStatus(str, Enum):
    """Status possíveis para um serviço"""
    STOPPED = "stopped"           # Serviço parado
    STARTING = "starting"         # Serviço iniciando
    RUNNING = "running"           # Serviço em execução
    STOPPING = "stopping"         # Serviço parando
    FAILED = "failed"            # Serviço falhou
    DEPENDENT_FAILED = "dependent_failed"  # Dependência falhou

class ServiceInfo:
    """Informações sobre um serviço"""
    def __init__(self, 
                 name: str, 
                 description: str,
                 dependencies: Optional[List[str]] = None,
                 required_ports: Optional[List[int]] = None):
        self.name = name
        self.description = description
        self.dependencies = dependencies or []
        self.required_ports = required_ports or []
        self.status = ServiceStatus.STOPPED
        self.last_status_change = datetime.now()
        self.error_message: Optional[str] = None
        self._lock = threading.Lock()
        self.logs: List[str] = []

    def update_status(self, status: ServiceStatus, error: Optional[str] = None):
        """Atualiza o status do serviço de forma thread-safe"""
        with self._lock:
            old_status = self.status
            self.status = status
            self.error_message = error
            self.last_status_change = datetime.now()
            
            # Registra a mudança de status
            log_msg = f"[{self.name}] Status alterado: {old_status} -> {status}"
            if error:
                log_msg += f" (Erro: {error})"
            self.add_log(log_msg)

    def add_log(self, message: str):
        """Adiciona uma mensagem ao log do serviço"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)  # Imprime no console para debug
        with self._lock:
            self.logs.append(log_entry)
            # Mantém apenas os últimos 1000 logs
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]

class ServiceManager:
    """Gerenciador de serviços"""
    def __init__(self):
        print("Inicializando ServiceManager...")
        self._services: Dict[str, ServiceInfo] = {}
        self._running_ports: Set[int] = set()
        self._lock = threading.Lock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = threading.Event()
        self._global_logs: List[str] = []
        print("ServiceManager inicializado com sucesso")

    def _add_global_log(self, message: str):
        """Adiciona uma mensagem ao log global"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(f"[ServiceManager] {log_entry}")
        with self._lock:
            self._global_logs.append(log_entry)
            if len(self._global_logs) > 1000:
                self._global_logs = self._global_logs[-1000:]

    def register_service(self, service: ServiceInfo) -> bool:
        """Registra um novo serviço"""
        try:
            self._add_global_log(f"Tentando registrar serviço: {service.name}")

            # Verifica se o serviço já existe
            if service.name in self._services:
                error_msg = f"Serviço {service.name} já registrado"
                self._add_global_log(f"Erro: {error_msg}")
                return False

            # Verifica se as dependências existem
            for dep in service.dependencies:
                if dep not in self._services:
                    error_msg = f"Dependência {dep} não encontrada para {service.name}"
                    self._add_global_log(f"Erro: {error_msg}")
                    return False

            # Verifica conflitos de porta
            for port in service.required_ports:
                if port in self._running_ports:
                    error_msg = f"Porta {port} já em uso (serviço: {service.name})"
                    self._add_global_log(f"Erro: {error_msg}")
                    return False

            # Registra o serviço
            with self._lock:
                self._services[service.name] = service

            self._add_global_log(f"Serviço {service.name} registrado com sucesso")
            return True

        except Exception as e:
            error_msg = f"Erro ao registrar serviço {service.name}: {str(e)}"
            self._add_global_log(f"Erro crítico: {error_msg}")
            self._add_global_log(f"Stacktrace: {traceback.format_exc()}")
            return False

    def start_service(self, name: str) -> bool:
        """Inicia um serviço e suas dependências"""
        try:
            self._add_global_log(f"Tentando iniciar serviço: {name}")

            service = self._services.get(name)
            if not service:
                self._add_global_log(f"Erro: Serviço {name} não encontrado")
                return False

            # Verifica se o serviço já está rodando
            if service.status in [ServiceStatus.RUNNING, ServiceStatus.STARTING]:
                self._add_global_log(f"Serviço {name} já está rodando ou iniciando")
                return True

            # Inicia dependências primeiro
            for dep in service.dependencies:
                self._add_global_log(f"Iniciando dependência {dep} para {name}")
                if not self.start_service(dep):
                    error_msg = f"Falha ao iniciar dependência {dep}"
                    service.update_status(ServiceStatus.DEPENDENT_FAILED, error_msg)
                    self._add_global_log(f"Erro: {error_msg}")
                    return False

            # Verifica portas
            with self._lock:
                for port in service.required_ports:
                    if port in self._running_ports:
                        error_msg = f"Porta {port} já em uso"
                        service.update_status(ServiceStatus.FAILED, error_msg)
                        self._add_global_log(f"Erro: {error_msg}")
                        return False
                    self._running_ports.add(port)

            # Inicia o serviço
            service.update_status(ServiceStatus.STARTING)
            self._add_global_log(f"Serviço {name} iniciando...")

            service.update_status(ServiceStatus.RUNNING)
            self._add_global_log(f"Serviço {name} iniciado com sucesso")
            return True

        except Exception as e:
            error_msg = f"Erro ao iniciar serviço {name}: {str(e)}"
            if service:
                service.update_status(ServiceStatus.FAILED, error_msg)
            self._add_global_log(f"Erro crítico: {error_msg}")
            self._add_global_log(f"Stacktrace: {traceback.format_exc()}")
            return False

    def stop_service(self, name: str) -> bool:
        """Para um serviço e seus dependentes"""
        try:
            self._add_global_log(f"Tentando parar serviço: {name}")

            service = self._services.get(name)
            if not service:
                self._add_global_log(f"Erro: Serviço {name} não encontrado")
                return False

            # Verifica se o serviço já está parado
            if service.status == ServiceStatus.STOPPED:
                self._add_global_log(f"Serviço {name} já está parado")
                return True

            # Para serviços dependentes primeiro
            for dep_name, dep_service in self._services.items():
                if name in dep_service.dependencies:
                    self._add_global_log(f"Parando serviço dependente {dep_name}")
                    if not self.stop_service(dep_name):
                        return False

            # Para o serviço
            service.update_status(ServiceStatus.STOPPING)
            self._add_global_log(f"Serviço {name} parando...")

            # Libera as portas
            with self._lock:
                for port in service.required_ports:
                    self._running_ports.discard(port)

            service.update_status(ServiceStatus.STOPPED)
            self._add_global_log(f"Serviço {name} parado com sucesso")
            return True

        except Exception as e:
            error_msg = f"Erro ao parar serviço {name}: {str(e)}"
            if service:
                service.update_status(ServiceStatus.FAILED, error_msg)
            self._add_global_log(f"Erro crítico: {error_msg}")
            self._add_global_log(f"Stacktrace: {traceback.format_exc()}")
            return False

    def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """Retorna o status atual de um serviço"""
        service = self._services.get(name)
        if service:
            self._add_global_log(f"Status do serviço {name}: {service.status}")
        else:
            self._add_global_log(f"Serviço {name} não encontrado")
        return service.status if service else None

    def list_services(self) -> Dict[str, ServiceInfo]:
        """Lista todos os serviços registrados"""
        self._add_global_log("Listando todos os serviços")
        return self._services.copy()

    def get_service_logs(self, name: str, last_n: int = 100) -> List[str]:
        """Retorna os últimos N logs de um serviço"""
        service = self._services.get(name)
        if not service:
            self._add_global_log(f"Tentativa de acessar logs do serviço inexistente: {name}")
            return []
        return service.logs[-last_n:]

    def get_global_logs(self, last_n: int = 100) -> List[str]:
        """Retorna os últimos N logs globais"""
        with self._lock:
            return self._global_logs[-last_n:]

    def start_monitor(self):
        """Inicia o monitoramento dos serviços"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._add_global_log("Monitor já está em execução")
            return

        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_services,
            daemon=True
        )
        self._monitor_thread.start()
        self._add_global_log("Monitor de serviços iniciado")

    def stop_monitor(self):
        """Para o monitoramento dos serviços"""
        if self._monitor_thread:
            self._add_global_log("Parando monitor de serviços...")
            self._stop_monitor.set()
            self._monitor_thread.join()
            self._add_global_log("Monitor de serviços parado")

    def _monitor_services(self):
        """Monitora o estado dos serviços"""
        while not self._stop_monitor.is_set():
            try:
                for name, service in self._services.items():
                    if service.status == ServiceStatus.RUNNING:
                        # Verifica se o serviço ainda está saudável
                        self._add_global_log(f"Verificando saúde do serviço: {name}")
                        # Aqui você implementaria a lógica de verificação específica
                        # para cada tipo de serviço

            except Exception as e:
                self._add_global_log(f"Erro no monitor de serviços: {str(e)}")
                self._add_global_log(f"Stacktrace: {traceback.format_exc()}")

            time.sleep(5)  # Verifica a cada 5 segundos

