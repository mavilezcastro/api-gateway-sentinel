"""
Rutas de autenticacion: login y token JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import obtener_configuracion
from app.core.seguridad import (autenticar_usuario, crear_token_acceso, obtener_usuario_actual)
from app.schemas.auth import TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticacion"])

@router.post("/login", response_model=TokenResponse)
async def login(formulario: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica al usuario y devuelve un JWT.

    Usa OAuth2PasswordRequestForm para compatibilidad con Swagger,
    Campos del form: username, password.
    """
    usuario = autenticar_usuario(formulario.username, formulario.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    config = obtener_configuracion()
    token = crear_token_acceso(usuario["username"])

    return TokenResponse(
        access_token=token,
        expira_en_minutos=config.jwt_expiracion_minutos,
    )

@router.get("/yo", response_model=UsuarioResponse)
async def obtener_usuario_logueado(
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Devuelve los datos del usuario autenticado (tura protegida de prueba)."""
    return UsuarioResponse(username=usuario["username"])