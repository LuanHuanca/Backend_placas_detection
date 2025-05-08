from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import CamaraCreate, Camara

router = APIRouter(prefix="/camaras", tags=["camaras"])

@router.post("/", response_model=Camara)
def create_camara(camara: CamaraCreate, db: Session = Depends(get_db)):
    db_camara = Camara(**camara.dict())
    db.add(db_camara)
    db.commit()
    db.refresh(db_camara)
    return db_camara

@router.get("/{camara_id}", response_model=Camara)
def get_camara(camara_id: int, db: Session = Depends(get_db)):
    camara = db.query(Camara).filter(Camara.id == camara_id).first()
    if not camara:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return camara

@router.get("/", response_model=list[Camara])
def get_all_camaras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Camara).offset(skip).limit(limit).all()