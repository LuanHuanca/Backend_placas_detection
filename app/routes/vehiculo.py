from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import VehiculoCreate, Vehiculo  # Esquemas Pydantic
from app.db.models import Vehiculo as VehiculoDB  # Modelo SQLAlchemy

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])

@router.post("/", response_model=Vehiculo)
def create_vehiculo(vehiculo: VehiculoCreate, db: Session = Depends(get_db)):
    db_vehiculo = VehiculoDB(**vehiculo.model_dump())
    db.add(db_vehiculo)
    db.commit()
    db.refresh(db_vehiculo)
    return Vehiculo.model_validate(db_vehiculo)  # Convertir a Pydantic

@router.get("/{vehiculo_id}", response_model=Vehiculo)
def get_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    vehiculo = db.query(VehiculoDB).filter(VehiculoDB.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return Vehiculo.model_validate(vehiculo)

@router.get("/", response_model=list[Vehiculo])
def get_all_vehiculos(db: Session = Depends(get_db)):
    vehiculos = db.query(VehiculoDB).all()
    return [Vehiculo.model_validate(v) for v in vehiculos]