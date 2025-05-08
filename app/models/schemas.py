from datetime import datetime
from typing import Union 
from pydantic import BaseModel

# Esquema para Cámaras
class CamaraBase(BaseModel):
    ubicacion: str
    descripcion: Union[str, None] = None
    ip_camara: str

class CamaraCreate(CamaraBase):
    pass

class Camara(CamaraBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Equivalente a orm_mode en Pydantic v2

# Esquema para Detecciones
class DeteccionBase(BaseModel):
    camara_id: Union[int, None] = None
    imagen_url: Union[str, None] = None
    confianza: Union[float, None] = None

class DeteccionCreate(DeteccionBase):
    placa_id: int

class Deteccion(DeteccionBase):
    id: int
    fecha_hora: datetime
    placa_id: int
    
    class Config:
        from_attributes = True

# Esquema para Placas
class PlacaBase(BaseModel):
    texto: str
    imagen_base64: str

class PlacaCreate(PlacaBase):
    vehiculo_id: Union[int, None] = None

class Placa(PlacaBase):
    id: int
    fecha_hora: datetime
    
    class Config:
        from_attributes = True

# Esquema para Vehículos 
class VehiculoBase(BaseModel):
    tipo_vehiculo: str
    marca: Union[str, None] = None
    color: Union[str, None] = None
    tipo: Union[str, None] = None

class VehiculoCreate(VehiculoBase):
    pass

class Vehiculo(VehiculoBase):
    id: int
    
    class Config:
        from_attributes = True

# Esquema para Alertas (FALTANTE)
class AlertaBase(BaseModel):
    tipo_alerta: Union[str, None] = None
    mensaje: Union[str, None] = None

class AlertaCreate(AlertaBase):
    deteccion_id: int

class Alerta(AlertaBase):
    id: int
    fecha_alerta: datetime
    
    class Config:
        from_attributes = True