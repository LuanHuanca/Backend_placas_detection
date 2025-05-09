from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from app.core.config import settings

# 1. Configura el esquema OAuth2 con la URL de obtención de tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # 2. Manejo de errores de autenticación
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 3. Decodificación y verificación del token JWT
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET,         # Clave secreta desde configuración
            algorithms=[settings.ALGORITHM]  # Algoritmo de encriptación (ej: HS256)
        )
        return payload  # 4. Devuelve el contenido del token si es válido
        
    except JWTError:  # 5. Captura errores de token inválido/expirado
        raise credentials_exception