# bot/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rpg_bot.db")

# The `connect_args={"check_same_thread": False}` is needed only for SQLite.
# It's not needed for other databases.
# StaticPool is used here for simplicity with SQLite in-memory for tests or simple deployments.
# For production, especially with other DBs, you'd use SQLAlchemy's default pool settings.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool # Good for :memory: or single-threaded CLI scripts
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    # This is where you would import your models before calling create_all
    # For example: from . import models
    # models.Base.metadata.create_all(bind=engine)
    # We will call this from main.py after models are defined.
    pass

def get_db():
    """Dependency injector for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example of how to use the session for CRUD operations (will be used in handlers)
# from .models import User
# def get_user(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()
