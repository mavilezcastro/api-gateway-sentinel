"""
Rutas de salud y eco para verificar el funcionamiento del gateway.
"""

from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["Salud"])


@router.get("/salud")
async def verificar_salud() -> dict[str, str]:
    """
    Endpoint de health check.

    Devuelve el estado del servicio. Útil para monitoreo y balanceadores de carga.
    """
    return {
        "estado": "ok",
        "servicio": "API Gateway & Sentinel",
    }


@router.post("/eco")
async def eco(datos: dict[str, Any]) -> dict[str, Any]:
    """
    Devuelve el JSON recibido sin modificarlo.

    Endpoint de prueba para validar que el filtro de inyección
    bloquea payloads maliciosos y deja pasar peticiones limpias.
    """
    return {
        "mensaje": "Petición recibida correctamente",
        "datos": datos,
    }
