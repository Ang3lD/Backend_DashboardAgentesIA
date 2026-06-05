"""
Router de autenticación.
Endpoints:
  POST /auth/login  — recibe form-data (OAuth2PasswordRequestForm) y devuelve JWT
  GET  /auth/me     — devuelve el perfil del usuario autenticado
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from src.infrastructure.database.config import get_db
from src.infrastructure.api.auth_schemas import TokenResponse, UserMe
from src.application.auth_service import (
    authenticate_user,
    create_access_token,
    decode_token,
    get_user_by_username,
    EXPIRE_SECS,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# Esquema OAuth2 — apunta al endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Dependencia reutilizable: usuario actual ─────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Decodifica el JWT del header Authorization: Bearer <token>
    y devuelve el usuario activo correspondiente.
    Lanza 401 si el token es inválido o el usuario no existe / está inactivo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


# ── Endpoints ────────────────────────────────────────────────────────────────

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión y obtener JWT",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Recibe `username` y `password` como form-data (estándar OAuth2).
    Devuelve un JWT Bearer si las credenciales son correctas.
    Devuelve 401 con mensaje genérico en caso contrario (no revela si el usuario existe).
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifica tu usuario y contraseña.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token, token_type="bearer", expires_in=EXPIRE_SECS)


@auth_router.get(
    "/me",
    response_model=UserMe,
    summary="Obtener perfil del usuario autenticado",
)
def me(current_user=Depends(get_current_user)):
    """Devuelve los datos del usuario correspondiente al JWT enviado."""
    return current_user
