"""
Middleware de rate limiting usando Redis.

Limita la cantidad de peticiones que una IP puede hacer
dentro de una ventana de tiempo configurable.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import obtener_configuracion
from app.core.redis_cliente import obtener_redis

PREFIJO_CLAVE = "rate_limit"

class LimitadorTasaMiddleware(BaseHTTPMiddleware):
    f"""
    Middleware que limita peticiones por IP usando redis.

    Algoritmo: ventana fija con INCR + EXPIRE.
    """
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        config = obtener_configuracion()
        redis = await obtener_redis()

        ip_cliente = request.client.host if request.client else "desconocida"
        clave = f"{PREFIJO_CLAVE}{ip_cliente}"

        # Incrementar contador (operacion atomica en Redis)
        contador = await redis.incr(clave)

        # Primera peticion de la ventana: establecer expiracion
        if contador == 1:
            await redis.expire(clave, config.ventana_segundos)

        # Verificar si supero el limite
        if contador > config.limite_peticiones:
            print(
                f"[SEGURIDAD] RATE LIMIT | IP={ip_cliente} |"
                f"CONTADOR={contador}/{config.limite_peticiones}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Demasiadas peticiones",
                    "detalle": (
                        f"Limite de {config.limite_peticiones} peticiones"
                        f"por {config.ventana_segundos} segundos superado"
                    ),
                    "reintentar_en_segundo": config.ventana_segundos,
                },
                headers={
                    "Retry-After": str(config.ventana_segundos),
                    "X-RateLimit-Limit": str(config.limite_peticiones),
                    "X-RateLimit-Remaining": str(
                        max(0, config.limite_peticiones - contador)
                    ),
                },
            )

        # Peticion dentro del limite: continuar
        respuesta = await call_next(request)

        # Agregar headers informativos a la respuesta existosa
        respuesta.headers["X-RateLimit-Limit"] = str(config.limite_peticiones)
        respuesta.headers["X-RateLimit-Remaining"] = str(
            max(0, config.limite_peticiones - contador)
        )
        return respuesta
    