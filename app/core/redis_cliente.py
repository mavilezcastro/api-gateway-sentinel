"""
Cliente Redis centralizado para rate limiting y otras operaciones en memoria.
"""
from redis.asyncio import Redis
from app.core.config import obtener_configuracion

_cliente_redis: Redis | None = None


async def obtener_redis() -> Redis:
    """
    Devuelve la conexion Redis (singleton).

    Crea la conexion la primera vez que se llama;
    las siguientes peticiones reutilizan la misma instancia.
    """
    global _cliente_redis
    if _cliente_redis is None:
        config = obtener_configuracion()
        _cliente_redis = Redis.from_url(
            config.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return _cliente_redis

async def cerrar_redis() -> None:
    """Cierra la conexion Redis al apagar la aplicacion."""
    global _cliente_redis
    if _cliente_redis is not None:
        await _cliente_redis.aclose()
        _cliente_redis = None