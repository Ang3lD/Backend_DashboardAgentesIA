"""
Servicio de autenticación: JWT + bcrypt.
Lee configuración desde variables de entorno para no exponer secretos en código.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.infrastructure.database.auth_models import User

# ── Configuración JWT (leer siempre desde variables de entorno) ──────────────
SECRET_KEY  = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING")
ALGORITHM   = "HS256"
EXPIRE_SECS = int(os.getenv("JWT_EXPIRE_SECONDS", "28800"))  # 8 horas por defecto


# ── Utilidades de contraseña ─────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Genera un hash bcrypt de la contraseña en texto plano."""
    # bcrypt requiere bytes para procesar el hash
    plain_bytes = plain.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica que una contraseña en texto plano coincide con el hash almacenado."""
    try:
        plain_bytes = plain.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False


# ── JWT ──────────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT firmado con el sub, iat y exp."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta if expires_delta else timedelta(seconds=EXPIRE_SECS))
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica y valida el JWT.
    Lanza JWTError si el token es inválido o ha expirado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ── Lógica de negocio ────────────────────────────────────────────────────────

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Busca al usuario por username y verifica su contraseña.
    Devuelve el objeto User si las credenciales son correctas, None en caso contrario.
    """
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        # Timing-safe dummy verify
        dummy_pwd = "$2b$12$DUMMY_SALT_FOR_TIMING_ATTACK_PROTECTION_DO_NOT_USE_IN_PROD"
        verify_password(password, dummy_pwd)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Obtiene un usuario activo por username."""
    return db.query(User).filter(User.username == username, User.is_active == True).first()


# ── Seed inicial ─────────────────────────────────────────────────────────────

def ensure_default_admin(db: Session) -> None:
    """
    Si no existe ningún usuario en la base de datos, crea un admin por defecto.
    Las credenciales por defecto se leen de variables de entorno.
    IMPORTANTE: cambiar ADMIN_USERNAME y ADMIN_PASSWORD en producción.
    """
    count = db.query(User).count()
    if count == 0:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin = User(
            username=admin_username,
            email=os.getenv("ADMIN_EMAIL", "admin@ambarrojo.com"),
            full_name="Administrador",
            hashed_password=hash_password(admin_password),
            is_active=True,
            is_admin=True,
        )
        db.add(admin)
        db.commit()
