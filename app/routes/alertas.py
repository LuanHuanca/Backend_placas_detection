from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import schemas

router = APIRouter(prefix="/alertas", tags=["alertas"])

@router.websocket("/ws")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Lógica de alertas en tiempo real
        await websocket.send_text(f"Alerta recibida: {data}")