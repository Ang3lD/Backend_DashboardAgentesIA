from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from src.infrastructure.database.config import Base


class User(Base):
    """
    Tabla de usuarios del panel de administración.
    Las contraseñas se almacenan SIEMPRE como hash bcrypt, nunca en texto plano.
    """
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(100), unique=True, index=True, nullable=False)
    email      = Column(String(255), unique=True, index=True, nullable=True)
    full_name  = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active  = Column(Boolean, default=True, nullable=False)
    is_admin   = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
