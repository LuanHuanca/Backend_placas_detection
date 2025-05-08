from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from .database import Base

class Camara(Base):
    __tablename__ = "camaras"
    id = Column(Integer, primary_key=True, index=True)
    ubicacion = Column(String(255))
    descripcion = Column(Text)
    ip_camara = Column(String(20))
    created_at = Column(DateTime)

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(100))
    color = Column(String(50))
    tipo = Column(String(50))
    tipo_vehiculo = Column(String(50))

class Placa(Base):
    __tablename__ = "placas"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String(20), unique=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    fecha_hora = Column(DateTime)
    imagen_base64 = Column(Text)

class Deteccion(Base):
    __tablename__ = "detecciones"
    id = Column(Integer, primary_key=True, index=True)
    placa_id = Column(Integer, ForeignKey("placas.id"))
    camara_id = Column(Integer, ForeignKey("camaras.id"))
    fecha_hora = Column(DateTime)
    imagen_url = Column(Text)
    confianza = Column(Float)

class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True, index=True)
    deteccion_id = Column(Integer, ForeignKey("detecciones.id"))
    tipo_alerta = Column(String(100))
    mensaje = Column(Text)
    fecha_alerta = Column(DateTime)