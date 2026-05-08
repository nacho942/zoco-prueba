# Prueba técnica – Zoco

Implementación de la prueba técnica para Zoco Compliance.

API simple para administrar bares/eventos de Tucumán, con:
- CRUD de lugares
- Carga automática desde una fuente mock (JSON)
- Lógica tipo “IA” para clasificar y detectar posibles duplicados

---

## Stack utilizado

- Python 3.13
- FastAPI + Uvicorn
- SQLAlchemy
- SQLite

Elegí este stack porque es liviano y rápido de levantar para una prueba.

---

## Cómo correr el proyecto

1. Clonar el repo:

```bash
git clone https://github.com/nacho942/zoco-prueba.git
cd zoco-prueba
