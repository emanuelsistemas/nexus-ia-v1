from core.services import ServiceManager, BackupService
import traceback

# Inicializa o gerenciador de serviços
service_manager = ServiceManager()

# Dicionário para manter referência aos serviços
services = {}

def initialize_services():
    """Inicializa todos os serviços"""
    try:
        print("Iniciando inicialização dos serviços...")

        # Inicializa o serviço de backup
        print("Criando instância do serviço de backup...")
        backup_service = BackupService("/data/backups")
        services["backup"] = backup_service

        # Registra o serviço
        print("Registrando serviço de backup...")
        if not service_manager.register_service(backup_service.info):
            raise Exception("Falha ao registrar serviço de backup")

        # Inicia o serviço
        print("Iniciando serviço de backup...")
        if not service_manager.start_service("backup"):
            raise Exception("Falha ao iniciar serviço de backup")

        # Inicia o monitoramento
        print("Iniciando monitoramento de serviços...")
        service_manager.start_monitor()

        print("Inicialização dos serviços concluída com sucesso")

    except Exception as e:
        print(f"Erro ao inicializar serviços: {e}")
        print("Stacktrace:")
        print(traceback.format_exc())
        raise

