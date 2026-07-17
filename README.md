# API Gateway & Sentinel

API Gateway minimalista con enfoque en ciberseguridad backend, construido con **Python 3.12**, **FastAPI** y **Redis**.

Proyecto de portfolio para demostrar conocimientos en desarrollo backend seguro, rate limiting, autenticación JWT y defensa contra inyecciones (OWASP Top 10).

## Características

| Estado | Feature |
|--------|---------|
| ✅ | Filtro de inyección SQL/NoSQL (middleware OWASP básico) |
| 🔜 | Rate limiting con Redis |
| 🔜 | Autenticación JWT |
| 🔜 | Logs de seguridad |
| 🔜 | Proxy gateway hacia microservicios |

## Requisitos

- Python 3.12+
- pip

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd api-gateway-sentinel

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux/macOS)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS
```

## Ejecución

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva: [http://localhost:8000/docs](http://localhost:8000/docs)

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/salud` | Verifica que el servicio está activo |
| POST | `/eco` | Devuelve el JSON recibido (útil para probar el filtro) |

## Probar el filtro de inyección

```bash
# Petición limpia (200 OK)
curl http://localhost:8000/salud

# Inyección en query string (403 Forbidden)
curl "http://localhost:8000/eco?usuario=admin' OR 1=1--"

# Inyección en body JSON (403 Forbidden)
curl -X POST http://localhost:8000/eco ^
  -H "Content-Type: application/json" ^
  -d "{\"nombre\": \"'; DROP TABLE usuarios;--\"}"
```

## Estructura del proyecto

```
app/
├── main.py                  # Punto de entrada FastAPI
├── core/
│   └── config.py            # Configuración centralizada
├── middleware/
│   └── filtro_inyeccion.py  # Filtro OWASP de inyección
└── api/
    └── rutas/
        └── salud.py         # Endpoints de prueba
```

## Roadmap

1. **Paso 1** — Estructura base + filtro de inyección ✅
2. **Paso 2** — Rate limiting con Redis
3. **Paso 3** — Autenticación JWT
4. **Paso 4** — Logs de seguridad
5. **Paso 5** — Proxy gateway real

## Licencia

MIT
