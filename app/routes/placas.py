from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import PlacaCreate, Placa  # Use Pydantic models
from app.db.models import Placa as PlacaModel  # Import SQLAlchemy model

router = APIRouter(prefix="/placas", tags=["placas"])

@router.post("/", response_model=Placa)
def create_placa(placa: PlacaCreate, db: Session = Depends(get_db)):
    db_placa = PlacaModel(**placa.dict())  # Create SQLAlchemy model instance
    db.add(db_placa)
    db.commit()
    db.refresh(db_placa)
    return Placa.from_orm(db_placa)  # Convert to Pydantic model

@router.get("/{placa_id}", response_model=Placa)
def get_placa(placa_id: int, db: Session = Depends(get_db)):
    placa = db.query(PlacaModel).filter(PlacaModel.id == placa_id).first()
    if not placa:
        raise HTTPException(status_code=404, detail="Placa no encontrada")
    return Placa.from_orm(placa)

@router.get("/", response_model=list[Placa])
def get_all_placas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    placas = db.query(PlacaModel).offset(skip).limit(limit).all()
    return [Placa.from_orm(placa) for placa in placas]