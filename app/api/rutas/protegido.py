"""
Rutas que requieren autenticacion JWT.
"""
from fastapi import APIRouter, Depends
from app.core.seguridad import obtener_usuario_actual

router = APIRouter(prefix="/protegido", tags=["Protegido"])

@router.get("/perfil")
async def obtener_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    """
    Ejemplo de ruta protegida
    
    Solo accseible con header: Authorization: Bearer <token>
    """
    return {
        "mensaje": "Acceso autorizado al recurso protegido",
        "usuario": usuario["username"],
    }