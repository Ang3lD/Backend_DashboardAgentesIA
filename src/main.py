from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.config import engine, Base
from src.infrastructure.api.routes import router as clients_router

# Creates the tables in the database the first time the app is run
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Clients and Agents API",
    description="Backend using Hexagonal Architecture, ready for PostgreSQL",
    version="1.0.0"
)

# Basic CORS configuration for Frontend connectivity (e.g., React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register our routes (endpoints) in the application
app.include_router(clients_router)

@app.get("/")
def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Hello! The backend API is running correctly. Visit /docs to see the documentation."}
