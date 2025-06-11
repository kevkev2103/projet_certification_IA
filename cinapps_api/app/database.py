# app/database.py

from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def check_db_connection():
    try:
        
        with engine.connect() as conn:
            print("✅ Connexion à MySQL réussie avec SQLAlchemy !")
    except Exception as e:
        print(f"❌ Erreur de connexion à MySQL : {e}")

def init_db():
    """Crée toutes les tables définies par les models SQLModel."""
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
