from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from . import models, schemas
from .database import engine, SessionLocal, Base
from . import ingest
from . import ai

# Crear tablas al iniciar la app
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependencia de sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "API funcionando para la prueba de Zoco"}


# Crear un lugar
@app.post("/places", response_model=schemas.Place)
def create_place(place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    db_place = models.Place(
        name=place.name,
        location=place.location,
        category=place.category,
        source=place.source,
        obtained_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


# Listar lugares
@app.get("/places", response_model=list[schemas.Place])
def list_places(db: Session = Depends(get_db)):
    places = db.query(models.Place).all()
    return places


# Editar lugar
@app.put("/places/{place_id}", response_model=schemas.Place)
def update_place(place_id: int, place: schemas.PlaceUpdate, db: Session = Depends(get_db)):
    db_place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")

    if place.name is not None:
        db_place.name = place.name
    if place.location is not None:
        db_place.location = place.location
    if place.category is not None:
        db_place.category = place.category
    if place.is_active is not None:
        db_place.is_active = place.is_active

    db_place.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_place)
    return db_place


# Desactivar lugar (soft delete)
@app.delete("/places/{place_id}")
def delete_place(place_id: int, db: Session = Depends(get_db)):
    db_place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")

    db_place.is_active = False
    db_place.updated_at = datetime.utcnow()
    db.commit()
    return {"detail": "Place deactivated"}


# Sync desde fuente mock
@app.post("/sync/mock")
def run_mock_sync(db: Session = Depends(get_db)):
    result = ingest.sync_from_mock(db)
    return result


# Endpoint para probar la "IA"
class AITestInput(BaseModel):
    name: str
    location: str


@app.post("/ai/test")
def test_ai(input_data: AITestInput, db: Session = Depends(get_db)):
    existing_places = (
        db.query(models.Place)
        .filter(models.Place.location == input_data.location)
        .all()
    )

    dup_info = ai.detectar_posible_duplicado(input_data.name, existing_places)
    category = ai.clasificar_lugar_por_nombre(input_data.name)

    return {
        "input_name": input_data.name,
        "location": input_data.location,
        "predicted_category": category,
        "duplicate_info": dup_info,
        "candidates_considered": [
            {"id": p.id, "name": p.name, "location": p.location}
            for p in existing_places
        ],
    }
