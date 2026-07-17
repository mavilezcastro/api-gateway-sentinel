# API Gateway & Sentinel

API Gateway minimalista con enfoque en **ciberseguridad backend**, construido con Python 3.12, FastAPI y Redis.

Proyecto de portfolio que demuestra capas de seguridad en un gateway: filtro de inyección (OWASP), rate limiting, autenticación JWT y arquitectura modular.

## Características implementadas

| Feature | Descripción |
|---------|-------------|
| Filtro de inyección | Middleware que analiza URL y body JSON bloqueando patrones SQL/NoSQL/XSS |
| Rate limiting | Límite de peticiones por IP usando Redis (ventana fija) |
| Autenticación JWT | Login con bcrypt + tokens Bearer con expiración |
| Rutas protegidas | Endpoints que requieren token válido |
| Docker | Redis 7 vía docker-compose |

## Stack tecnológico

- **Python 3.12** · **FastAPI** · **Redis** · **JWT (python-jose)** · **bcrypt (passlib)** · **Docker**

## Requisitos previos

- Python 3.12+
- Docker Desktop (para Redis)
- Git

## Instalación

```bash
git clone https://github.com/mavilezcastro/api-gateway-sentinel.git
cd api-gateway-sentinel

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS
```

Edita `.env` y asigna un `JWT_SECRETO` único (puedes generarlo con `openssl rand -hex 32`).

## Ejecución

```bash
# 1. Levantar Redis
docker compose up -d

# 2. Arrancar el gateway
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/salud

> **Nota:** Usa `localhost` o `127.0.0.1` en el navegador, no `0.0.0.0`.

## Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/salud` | No | Health check |
| POST | `/eco` | No | Eco del JSON recibido |
| POST | `/auth/login` | No | Login (devuelve JWT) |
| GET | `/auth/yo` | Sí | Usuario autenticado |
| GET | `/protegido/perfil` | Sí | Ruta protegida de ejemplo |

**Usuario demo:** `admin` / `Sentinel2024!`

## Pruebas rápidas

### Rate limiting (5 peticiones/min)

```powershell
1..6 | ForEach-Object {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/salud" -UseBasicParsing
        Write-Host "Petición $_`: $($r.StatusCode)"
    } catch {
        Write-Host "Petición $_`: $($_.Exception.Response.StatusCode.value__)"
    }
}
```

Esperado: 5× `200`, luego `429`.

### Login JWT

```powershell
curl.exe -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=Sentinel2024!"
```

### Ruta protegida

```powershell
$token = "PEGA_AQUI_EL_ACCESS_TOKEN"
curl.exe http://localhost:8000/protegido/perfil -H "Authorization: Bearer $token"
```

### Filtro de inyección (403)

```powershell
curl.exe "http://localhost:8000/eco?usuario=admin' OR 1=1--"
```

## Arquitectura

```
Cliente → Rate Limiter → Filtro Inyección → Rutas FastAPI
                ↓                                    ↓
              Redis                          JWT en rutas protegidas
```

## Estructura del proyecto

```
app/
├── main.py
├── core/
│   ├── config.py          # Configuración (.env)
│   ├── redis_cliente.py   # Conexión Redis
│   └── seguridad.py       # JWT + bcrypt
├── middleware/
│   ├── filtro_inyeccion.py
│   └── limitador_tasa.py
├── api/rutas/
│   ├── salud.py
│   ├── auth.py
│   └── protegido.py
└── schemas/
    └── auth.py
pruebas/
docker-compose.yml
```

## Roadmap futuro

- [ ] Logs de seguridad en archivo
- [ ] Proxy gateway hacia microservicios
- [ ] Excluir `/docs` del rate limiter

## Autor

**Manuel Avilez** — Backend Developer Junior | Estudiante de Ciberseguridad

## Licencia

MIT
