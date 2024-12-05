from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from core.services import ServiceManager, BackupService, ServiceStatus
from core.services.service_registry import service_manager, services, initialize_services
import os
import traceback

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de resposta
class ServiceStatusResponse(BaseModel):
    name: str
    status: ServiceStatus
    description: str
    error_message: Optional[str] = None

class ServiceMetricsResponse(BaseModel):
    name: str
    metrics: Dict[str, Any]

# Registra e inicia os serviços
@app.on_event("startup")
async def startup_event():
    print("Iniciando evento de startup...")
    try:
        print("Inicializando serviços...")
        initialize_services()
        print("Serviços inicializados com sucesso")
    except Exception as e:
        print(f"Erro durante inicialização: {e}")
        print("Stacktrace:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Falha na inicialização: {str(e)}"
        )

# Endpoint para listar status dos serviços
@app.get("/api/v1/services/status", response_model=List[ServiceStatusResponse])
async def list_services_status():
    """Lista o status de todos os serviços"""
    response = []
    for service_info in service_manager.list_services().values():
        response.append({
            "name": service_info.name,
            "status": service_info.status,
            "description": service_info.description,
            "error_message": service_info.error_message
        })
    return response

# Endpoint para obter métricas dos serviços
@app.get("/api/v1/services/metrics", response_model=List[ServiceMetricsResponse])
async def get_services_metrics():
    """Obtém métricas de todos os serviços"""
    response = []
    for name, service in services.items():
        metrics = await service.get_metrics()
        response.append({
            "name": name,
            "metrics": metrics
        })
    return response

# Endpoint para obter logs de um serviço específico
@app.get("/api/v1/services/{service_name}/logs")
async def get_service_logs(service_name: str, last_n: int = 100):
    """Obtém os últimos N logs de um serviço específico"""
    logs = service_manager.get_service_logs(service_name, last_n)
    if not logs:
        raise HTTPException(
            status_code=404,
            detail=f"Serviço {service_name} não encontrado ou sem logs"
        )
    return {"logs": logs}

# Endpoint para obter logs globais do gerenciador de serviços
@app.get("/api/v1/services/logs")
async def get_global_logs(last_n: int = 100):
    """Obtém os últimos N logs globais do gerenciador de serviços"""
    return {"logs": service_manager.get_global_logs(last_n)}

# Endpoint de health check
@app.get("/health")
async def health_check():
    """Verifica a saúde da aplicação"""
    print("Executando health check...")
    try:
        # Verifica todos os serviços
        all_healthy = True
        service_status = {}

        for name, service in services.items():
            print(f"Verificando serviço {name}...")
            is_healthy = await service.health_check()
            service_status[name] = "healthy" if is_healthy else "unhealthy"
            if not is_healthy:
                all_healthy = False

        response = {
            "status": "healthy" if all_healthy else "unhealthy",
            "version": "1.0.0",
            "environment": "development",
            "services": service_status
        }
        print(f"Health check concluído: {response}")
        return response
    except Exception as e:
        print(f"Erro durante health check: {e}")
        print("Stacktrace:")
        print(traceback.format_exc())
        raise

# Registra as rotas dos módulos
print("Registrando rotas...")
from routers import backup
app.include_router(backup.router, prefix="/api/v1/backup", tags=["backup"])
print("Rotas registradas com sucesso")

