import json
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from . import models
from . import ai

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tucuman_bares.json"


def fetch_from_mock():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sync_from_mock(db: Session):
    items = fetch_from_mock()
    inserted = 0
    updated = 0

    for item in items:
        name = item["name"]
        location = item["location"]
        source = item.get("source", "mock")

        # obtengo candidatos existentes en la misma ciudad
        existing_places = (
            db.query(models.Place)
            .filter(models.Place.location == location)
            .all()
        )

        dup_info = ai.detectar_posible_duplicado(name, existing_places)
        category = ai.clasificar_lugar_por_nombre(name)

        if dup_info["es_duplicado"]:
            # actualizar el existente
            place = (
                db.query(models.Place)
                .filter(models.Place.id == dup_info["id_duplicado"])
                .first()
            )
            if place:
                place.category = category
                place.source = source
                place.updated_at = datetime.now(timezone.utc)
                updated += 1
        else:
            # crear nuevo
            place = models.Place(
                name=name,
                location=location,
                category=category,
                source=source,
                obtained_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(place)
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": updated}
