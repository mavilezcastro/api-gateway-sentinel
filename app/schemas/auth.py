"""
Esquemas Pydantic para autenticacion.
"""

from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """Credenciales de login."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class TokenResponse(BaseModel):
    """Respuesta con el token JWT."""

    access_token: str
    token_type: str ="bearer"
    expira_en_minutos: int

class UsuarioResponse(BaseModel):
    """Datos publicos del usuario autenticado."""

    username: str