from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database connection URL (Make sure it matches your docker-compose config)
DATABASE_URL = "postgresql://postgres:Smartchoice1!@db:5432/innersense"#os.getenv("DATABASE_URL", "postgresql://postgres:Smartchoice1!@db:5432/innersense")
# Create synchronous engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()