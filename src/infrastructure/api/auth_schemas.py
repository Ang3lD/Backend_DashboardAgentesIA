from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """Respuesta del endpoint /auth/login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class UserMe(BaseModel):
    """Datos del usuario autenticado — endpoint /auth/me."""
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_admin: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
