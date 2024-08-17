# Biblioteca estándar
from datetime import datetime, timedelta, timezone
from typing import Annotated
import os

# Terceros
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Local
from schemas import TokenData
from database import SessionLocal
from models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# Dependencia para obtener la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# Verifica que una contraseña en texto plano coincida con una contraseña cifrada
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Genera un hash a partir de una contraseña en texto plano
def get_password_hash(password):
    return pwd_context.hash(password)


# Obtiene un usuario de la base de datos dado su nombre de usuario
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Autentica a un usuario verificando su contraseña
def authenticate_user(db: db_dependency, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Crea un token de acceso JWT con una expiración opcional
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Obtiene el usuario actual autenticado a partir del token de acceso
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")

        if not username or not id:
            raise credentials_exception

        token_data = TokenData(username=username, id=id)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


# Verifica si el usuario actual está activo
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


user_dependency = Annotated[User, Depends(get_current_active_user)]