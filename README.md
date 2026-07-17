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
