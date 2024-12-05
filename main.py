from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import backup
import uvicorn
import os

app = FastAPI(
    title="Nexus IA v1",
    description="Sistema de Backup e Gerenciamento de IA",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas
app.include_router(backup.router, prefix="/api/v1")

# Rota de health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    # Configurações do servidor
    port = int(os.getenv("PORT", 8001))
    log_level = os.getenv("LOG_LEVEL", "info")

    # Inicia o servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=True  # Apenas em desenvolvimento
    )

