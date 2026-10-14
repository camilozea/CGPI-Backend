import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.business import Business
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from app.dependencies import get_current_user
from app.services.activity import log_activity

router = APIRouter(prefix="/auth", tags=["auth"])


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, pwd_hash = stored.split("$")
    new_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return new_hash.hex() == pwd_hash


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(
        (User.usuario == user_data.usuario) | (User.correo == user_data.correo)
    ))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o correo ya existe")

    from app.schemas.user import VALID_ROLES

    is_first = await db.scalar(select(func.count(User.id))) == 0

    role = "admin" if is_first else user_data.role
    if role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido")

    hashed = hash_password(user_data.contrasena)
    user = User(
        name=user_data.name,
        apellido=user_data.apellido,
        correo=user_data.correo,
        usuario=user_data.usuario,
        contrasena=hashed,
        role=role,
        business_id=user_data.business_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await log_activity(
        db, user.id, f"{user.name} {user.apellido}",
        "register", "user", user.id,
        f"Usuario registrado: {user.usuario}",
    )
    return user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.usuario == login_data.usuario))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.contrasena, user.contrasena):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada. Contacta al administrador")

    if user.role == "propietario" and user.business_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Propietario no vinculado a un negocio. Contacta al administrador",
        )

    token = create_access_token({"sub": str(user.id)})

    await log_activity(
        db, user.id, f"{user.name} {user.apellido}",
        "login", "user", user.id,
        f"Inicio de sesión: {user.usuario}",
    )
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/my-business")
async def get_my_business(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.business_id:
        return {"id": None, "name": None, "type": None}
    result = await db.execute(select(Business).where(Business.id == current_user.business_id))
    business = result.scalar_one_or_none()
    if not business:
        return {"id": None, "name": None, "type": None}
    return {"id": business.id, "name": business.name, "type": business.type}
