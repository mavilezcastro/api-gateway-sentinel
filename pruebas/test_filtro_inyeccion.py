"""
Pruebas del filtro de inyección.

Ejecutar con: pytest pruebas/ -v
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def cliente():
    """Cliente HTTP asíncrono para probar la aplicación."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_salud_retorna_ok(cliente):
    """GET /salud debe responder 200 con estado ok."""
    respuesta = await cliente.get("/salud")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "ok"


@pytest.mark.asyncio
async def test_eco_peticion_limpia(cliente):
    """POST /eco con JSON limpio debe responder 200."""
    respuesta = await cliente.post(
        "/eco",
        json={"nombre": "Antonio", "edad": 25},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["datos"]["nombre"] == "Antonio"


@pytest.mark.asyncio
async def test_bloquea_inyeccion_sql_en_cuerpo(cliente):
    """POST /eco con inyección SQL en el cuerpo debe responder 403."""
    respuesta = await cliente.post(
        "/eco",
        json={"nombre": "'; DROP TABLE usuarios;--"},
    )
    assert respuesta.status_code == 403
    datos = respuesta.json()
    assert "bloqueada" in datos["error"].lower()


@pytest.mark.asyncio
async def test_bloquea_inyeccion_sql_en_url(cliente):
    """Query string con inyección SQL debe responder 403."""
    respuesta = await cliente.get("/eco?usuario=admin' OR 1=1--")
    assert respuesta.status_code == 403


@pytest.mark.asyncio
async def test_bloquea_inyeccion_nosql(cliente):
    """POST /eco con operador NoSQL debe responder 403."""
    respuesta = await cliente.post(
        "/eco",
        json={"filtro": {"$where": "1==1"}},
    )
    assert respuesta.status_code == 403
