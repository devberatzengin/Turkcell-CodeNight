from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
# Support either a SQLAlchemy-style DATABASE_URL or a JDBC_URL provided by the user.
raw_db = os.getenv("DATABASE_URL") or os.getenv("JDBC_URL")
if raw_db is None:
    DATABASE_URL = "sqlite:///./dev.db"
else:
    # If JDBC URL was provided (jdbc:postgresql://...), convert to SQLAlchemy form
    if raw_db.startswith("jdbc:"):
        DATABASE_URL = raw_db.replace("jdbc:", "", 1)
    else:
        DATABASE_URL = raw_db

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
