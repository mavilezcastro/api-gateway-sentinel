"""
Configuración centralizada de la aplicación.

Usa pydantic-settings para cargar variables de entorno con validación de tipos.
"""

import re
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Patrones por defecto de inyección SQL, NoSQL y XSS básico
PATRONES_INYECCION_DEFECTO: list[str] = [
    # SQL Injection
    r"select\s+.*\s+from",
    r"union\s+select",
    r"drop\s+table",
    r"insert\s+into",
    r"delete\s+from",
    r"update\s+.*\s+set",
    r"or\s+1\s*=\s*1",
    r"'\s*or\s*'",
    r"--\s*$",
    r";\s*--",
    r"'\s*;\s*",
    # NoSQL Injection
    r"\$where",
    r"\$gt",
    r"\$ne",
    r"\$regex",
    r"\{\s*\$",
    # XSS básico
    r"<script\b",
    r"javascript\s*:",
]


class Configuracion(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    nombre_app: str = "API Gateway & Sentinel"
    version: str = "0.1.0"
    modo_debug: bool = True
    patrones_inyeccion: list[str] = PATRONES_INYECCION_DEFECTO
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    # Rate limiting
    limite_peticiones: int = 5 # Maximo de peticiones por ventana
    ventana_segundos: int = 60 # Duracion de la ventana(1 minuto)
    # JWT
    jwt_secreto: str = "CAMBIAR-EN-PRODUCCION-usar-env"
    jwt_algoritmo: str = "HS256"
    jwt_expiracion_minutos: int = 15 


    @field_validator("patrones_inyeccion", mode="before")
    @classmethod
    def parsear_patrones(cls, valor: str | list[str]) -> list[str]:
        """Convierte una cadena separada por comas en lista de patrones regex."""
        if isinstance(valor, str):
            return [p.strip() for p in valor.split(",") if p.strip()]
        return valor

    def obtener_regex_compiladas(self) -> list[re.Pattern[str]]:
        """Compila los patrones de inyección para uso eficiente en el middleware."""
        return [
            re.compile(patron, re.IGNORECASE)
            for patron in self.patrones_inyeccion
        ]


@lru_cache
def obtener_configuracion() -> Configuracion:
    """
    Devuelve una instancia única (singleton) de la configuración.

    @lru_cache evita re-leer el archivo .env en cada petición.
    """
    return Configuracion()
