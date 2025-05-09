from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Camara as CamaraDB  
from app.models.schemas import CamaraCreate, Camara

router = APIRouter(prefix="/camaras", tags=["camaras"])

@router.post("/", response_model=Camara)
def create_camara(camara: CamaraCreate, db: Session = Depends(get_db)):
    db_camara = CamaraDB(**camara.model_dump())
    db.add(db_camara)
    db.commit()
    db.refresh(db_camara)  
    return Camara.model_validate(db_camara)

@router.get("/{camara_id}", response_model=Camara)
def get_camara(camara_id: int, db: Session = Depends(get_db)):
    camara = db.query(CamaraDB).filter(CamaraDB.id == camara_id).first()
    
    if not camara:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    return Camara.model_validate(camara)
@router.get("/", response_model=list[Camara])
def get_all_camaras(db: Session = Depends(get_db)):
    camaras_db = db.query(CamaraDB).all()
    return [Camara.model_validate(c) for c in camaras_db]