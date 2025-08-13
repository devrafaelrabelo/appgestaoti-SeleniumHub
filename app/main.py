from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio


# Routers
from app.controllers import (
    cpf_controller,
    intranet_controller,
    ezchat_controller,
    ironvox_controller,
    health_controller,
    webassist_controller
)

# Middleware
from app.middleware.jwt_auth_middleware import AuthMiddleware

# Serviço de health
from app.services.health_service import atualizar_health_cache

from app.utils.lifecycle import startup_time

app = FastAPI(
    title="Automação API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de autenticação
app.add_middleware(AuthMiddleware)

# Prefixo global da API
API_PREFIX = "/selenium"

# Rotas
app.include_router(cpf_controller.router, prefix=f"{API_PREFIX}/cpf", tags=["Consulta CPF"])
app.include_router(intranet_controller.router, prefix=f"{API_PREFIX}/intranet", tags=["Cadastro Intranet"])
app.include_router(ezchat_controller.router, prefix=f"{API_PREFIX}/ezchat", tags=["Consulta EzChat"])
app.include_router(ironvox_controller.router, prefix=f"{API_PREFIX}/ironvox", tags=["IronVox"])
app.include_router(webassist_controller.router, prefix=f"{API_PREFIX}/webassist", tags=["WebAssist"])
app.include_router(health_controller.router, prefix=API_PREFIX)


# Inicia o loop assíncrono de atualização de health
@app.on_event("startup")
async def iniciar_monitoramento_health():
    asyncio.create_task(health_loop())

async def health_loop():
    while True:
        await atualizar_health_cache()
        await asyncio.sleep(10)
