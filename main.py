from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from core.services import ServiceManager, BackupService, ServiceStatus
from core.services.service_registry import service_manager, services, initialize_services
from routers import backup
import os
import traceback
import sys

# Configuração de logging detalhado
print("=== INICIANDO APLICAÇÃO ===\n", file=sys.stderr)

app = FastAPI(debug=True)  # Ativando modo debug

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
app.include_router(backup.router, prefix="/api/v1/backup", tags=["backup"])

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
    print("=== EVENTO DE STARTUP INICIADO ===", file=sys.stderr)
    try:
        print("Inicializando serviços...", file=sys.stderr)
        initialize_services()
        print("Serviços inicializados com sucesso", file=sys.stderr)
    except Exception as e:
        print(f"ERRO CRÍTICO durante inicialização: {e}", file=sys.stderr)
        print("Stacktrace:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise

# Endpoint de health check com logs detalhados
@app.get("/health")
async def health_check():
    print("=== HEALTH CHECK INICIADO ===", file=sys.stderr)
    try:
        # Verifica todos os serviços
        all_healthy = True
        service_status = {}

        print("Verificando serviços...", file=sys.stderr)
        for name, service in services.items():
            print(f"Verificando serviço {name}...", file=sys.stderr)
            try:
                is_healthy = await service.health_check()
                service_status[name] = "healthy" if is_healthy else "unhealthy"
                if not is_healthy:
                    all_healthy = False
                print(f"Serviço {name}: {service_status[name]}", file=sys.stderr)
            except Exception as e:
                print(f"Erro ao verificar serviço {name}: {e}", file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
                service_status[name] = "error"
                all_healthy = False

        response = {
            "status": "healthy" if all_healthy else "unhealthy",
            "version": "1.0.0",
            "environment": "development",
            "services": service_status
        }
        print(f"Health check concluído: {response}", file=sys.stderr)
        return response
    except Exception as e:
        print(f"ERRO CRÍTICO durante health check: {e}", file=sys.stderr)
        print("Stacktrace:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise

# Endpoint para listar status dos serviços
@app.get("/api/v1/services/status", response_model=List[ServiceStatusResponse])
async def list_services_status():
    """Lista o status de todos os serviços"""
    print("=== LISTANDO STATUS DOS SERVIÇOS ===", file=sys.stderr)
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
    print("=== OBTENDO MÉTRICAS DOS SERVIÇOS ===", file=sys.stderr)
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
    print(f"=== OBTENDO LOGS DO SERVIÇO {service_name} ===", file=sys.stderr)
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
    print("=== OBTENDO LOGS GLOBAIS ===", file=sys.stderr)
    return {"logs": service_manager.get_global_logs(last_n)}

print("=== APLICAÇÃO CONFIGURADA COM SUCESSO ===\n", file=sys.stderr)

