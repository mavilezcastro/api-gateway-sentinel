"""
Utilidades de seguridad: hash de contraseñas, JWT, dependencias de auth.
"""

from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import obtener_configuracion

# Conexto bycrypt para hashear contraseñas
contexto_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Extre el token del header: Authorization: Bearer <token>
oauth2_esquema = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Usuario demo en memoria(en produccion: base de datos)
# Password demo: Sentinel2024!
# Genera el has una vez con: contexto_hash.hash("Sentinel2024!")
USUARIOS_DEMO: dict[str, dict[str, str]] = {
    "admin": {
        "username" : "admin",
        "hash_contraseña": "$2b$12$H6KbaU0T0qqPiTKDrrO0ZOdLjJaPMko7wlCgC7nitymvaneIQmvmS",
    }
}

def verificar_contraseña(contraseña_plana: str, hash_contraseña: str) -> bool:
    """Compara contraseña en texto plano con su hash bycrypt."""
    return contexto_hash.verify(contraseña_plana, hash_contraseña)

def autenticar_usuario(username: str, password: str) -> dict | None:
    """
    Valida credenciales contra el almacen demo.

    Returns:
        Datos del usuario si son validas, None si no.
    """
    usuario = USUARIOS_DEMO.get(username)
    if not usuario:
        return None
    if not verificar_contraseña(password, usuario["hash_contraseña"]):
        return None
    return {"username": usuario["username"]}

def crear_token_acceso(username: str) -> str:
    """
    Genera un JWT firmado con expiracion.

    Payload:
        sub: username
        exp: timestamp de expiracion(UTC)
    """
    config = obtener_configuracion()
    expira= datetime.now(timezone.utc) + timedelta(
        minutes=config.jwt_expiracion_minutos
    )
    payload = {
        "sub": username,
        "exp": expira,
    }
    return jwt.encode(
        payload,
        config.jwt_secreto,
        algorithm=config.jwt_algoritmo,
    )

async def obtener_usuario_actual(token: str = Depends(oauth2_esquema)) -> dict:
    """
    Dependencia FastAPI: extrae y valida el JWT de cada peticion protegida.

    Raises:
        HTTPException 401 si el token es invalido o expiro.
    """
    config = obtener_configuracion()
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload =jwt.decode(
            token,
            config.jwt_secreto,
            algorithms=[config.jwt_algoritmo],
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credenciales_invalidas
    except JWTError:
        raise credenciales_invalidas

    usuario = USUARIOS_DEMO.get(username)
    if usuario is None:
        raise credenciales_invalidas

    return {"username": username}