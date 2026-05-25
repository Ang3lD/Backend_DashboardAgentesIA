from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection configuration
# This URL points to the local PostgreSQL database "agency_dashboard"
# Change "postgres:postgres" to your actual local username and password if different.
# When deploying to Hostinger VPS, update this URL with the production credentials.
SQLALCHEMY_DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/agency_dashboard"

# If you ever need to test with SQLite again, uncomment this line:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency that creates a new database session for each request,
    and ensures it's closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
