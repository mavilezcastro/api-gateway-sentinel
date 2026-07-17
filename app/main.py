"""
Punto de entrada de la aplicación API Gateway & Sentinel.

Ejecutar con:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager 

from fastapi import FastAPI

from app.api.rutas import salud, auth, protegido
from app.core.config import obtener_configuracion
from app.core.redis_cliente import cerrar_redis
from app.middleware.filtro_inyeccion import FiltroInyeccionMiddleware
from app.middleware.limitador_tasa import LimitadorTasaMiddleware



config = obtener_configuracion()

@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    """Gestiona recursos al arrancar y apagar la aplicacion."""
    yield
    await cerrar_redis()


app = FastAPI(
    title=config.nombre_app,
    version=config.version,
    description=(
        "API Gateway minimalista con enfoque en ciberseguridad backend. "
        "Incluye filtro de inyección OWASP, rate limiting y autenticación JWT."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=ciclo_vida,
)

# Registrar middleware de seguridad (se ejecuta ANTES de las rutas)
app.add_middleware(FiltroInyeccionMiddleware)
app.add_middleware(LimitadorTasaMiddleware)


# Registrar rutas
app.include_router(salud.router)
app.include_router(auth.router)
app.include_router(protegido.router)
