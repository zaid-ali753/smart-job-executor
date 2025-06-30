from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@db:5432/taskdb"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,         
    max_overflow=30,     
    pool_timeout=30,  
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)