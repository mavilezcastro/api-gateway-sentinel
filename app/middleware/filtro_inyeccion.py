"""
Middleware de filtro de inyección SQL/NoSQL (OWASP Top 10).

Analiza la URL y el cuerpo JSON de cada petición antes de que llegue
a las rutas de la aplicación.
"""

import json
import re
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import obtener_configuracion

# Métodos HTTP que pueden llevar cuerpo JSON
METODOS_CON_CUERPO = {"POST", "PUT", "PATCH"}


def contiene_inyeccion(
    texto: str,
    patrones: list[re.Pattern[str]],
) -> str | None:
    """
    Verifica si un texto contiene algún patrón de inyección.

    Args:
        texto: Cadena a analizar.
        patrones: Lista de expresiones regulares compiladas.

    Returns:
        El patrón que coincidió, o None si el texto es limpio.
    """
    for patron in patrones:
        if patron.search(texto):
            return patron.pattern
    return None


def analizar_valor(
    valor: Any,
    patrones: list[re.Pattern[str]],
) -> str | None:
    """
    Analiza recursivamente un valor JSON (string, dict, list) buscando inyecciones.

    Args:
        valor: Valor JSON a inspeccionar (puede ser anidado).
        patrones: Lista de expresiones regulares compiladas.

    Returns:
        El patrón que coincidió, o None si el valor es limpio.
    """
    if isinstance(valor, str):
        return contiene_inyeccion(valor, patrones)

    if isinstance(valor, dict):
        for clave, subvalor in valor.items():
            resultado = analizar_valor(clave, patrones)
            if resultado:
                return resultado
            resultado = analizar_valor(subvalor, patrones)
            if resultado:
                return resultado

    if isinstance(valor, list):
        for item in valor:
            resultado = analizar_valor(item, patrones)
            if resultado:
                return resultado

    return None


class FiltroInyeccionMiddleware(BaseHTTPMiddleware):
    """
    Middleware que intercepta peticiones y bloquea contenido sospechoso.

    Hereda de BaseHTTPMiddleware (Starlette), que proporciona el método
    dispatch() para procesar cada petición entrante.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        config = obtener_configuracion()
        patrones = config.obtener_regex_compiladas()
        ip_cliente = request.client.host if request.client else "desconocida"

        # 1. Analizar URL completa (path + query string)
        url_completa = str(request.url)
        patron_detectado = contiene_inyeccion(url_completa, patrones)
        if patron_detectado:
            return self._respuesta_bloqueo(
                ip=ip_cliente,
                tipo="inyeccion_url",
                detalle=patron_detectado,
                ubicacion=url_completa,
            )

        # 2. Analizar cuerpo JSON en métodos con cuerpo
        if request.method in METODOS_CON_CUERPO:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                cuerpo = await request.body()
                if cuerpo:
                    try:
                        datos = json.loads(cuerpo)
                    except json.JSONDecodeError:
                        return self._respuesta_bloqueo(
                            ip=ip_cliente,
                            tipo="json_invalido",
                            detalle="El cuerpo no es JSON válido",
                            ubicacion=request.url.path,
                        )

                    patron_detectado = analizar_valor(datos, patrones)
                    if patron_detectado:
                        return self._respuesta_bloqueo(
                            ip=ip_cliente,
                            tipo="inyeccion_cuerpo",
                            detalle=patron_detectado,
                            ubicacion=request.url.path,
                        )

                    # Reinyectar el cuerpo para que las rutas puedan leerlo
                    request = self._reinyectar_cuerpo(request, cuerpo)

        # 3. Petición limpia: continuar al siguiente handler
        return await call_next(request)

    def _reinyectar_cuerpo(self, request: Request, cuerpo: bytes) -> Request:
        """
        Crea una nueva Request con el cuerpo disponible de nuevo.

        Starlette consume el body al leerlo; sin esto, FastAPI no podría
        parsear el JSON en el endpoint.
        """
        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": cuerpo, "more_body": False}

        return Request(request.scope, receive)

    def _respuesta_bloqueo(
        self,
        ip: str,
        tipo: str,
        detalle: str,
        ubicacion: str,
    ) -> JSONResponse:
        """
        Genera respuesta 403 y registra el bloqueo en consola.

        En pasos futuros, este registro se moverá a un archivo de logs.
        """
        print(
            f"[SEGURIDAD] BLOQUEADO | IP={ip} | Tipo={tipo} | "
            f"Detalle={detalle} | Ubicación={ubicacion}"
        )

        return JSONResponse(
            status_code=403,
            content={
                "error": "Petición bloqueada por el filtro de seguridad",
                "tipo": tipo,
                "detalle": "Se detectó contenido potencialmente malicioso",
            },
        )
