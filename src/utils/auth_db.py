import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Text, desc
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    os.makedirs("data", exist_ok=True)
    DB_PATH = "sqlite:///./data/users.db"
    engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    print("Using LOCAL SQLite database.")
else:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Checks if connection is alive before using it
        pool_recycle=300     # Refreshes connections every 5 minutes
    )
    print("Using CLOUD PostgreSQL database.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    type = Column(String)
    timestamp = Column(String)
    inputs = Column(Text)  # JSON stored as Text for compatibility
    results = Column(Text) # JSON stored as Text


def init_db():
    """Creates tables if they don't exist. Called by main.py on startup."""
    Base.metadata.create_all(bind=engine)


def save_history(email, analysis_type, inputs, results):
    session = SessionLocal()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Convert dicts to JSON strings for storage
        inputs_json = json.dumps(inputs)
        results_json = json.dumps(results)
        
        record = History(
            user_email=email, 
            type=analysis_type, 
            timestamp=timestamp, 
            inputs=inputs_json, 
            results=results_json
        )
        session.add(record)
        session.commit()
    finally:
        session.close()

def get_history(email):
    session = SessionLocal()
    try:
        # Fetch last 20 records, newest first
        rows = session.query(History).filter(History.user_email == email).order_by(desc(History.id)).limit(20).all()
        
        return [
            {
                "id": r.id,
                "type": r.type,
                "timestamp": r.timestamp,
                "inputs": json.loads(r.inputs),
                "results": json.loads(r.results)
            } for r in rows
        ]
    finally:
        session.close()

def delete_history(email):
    session = SessionLocal()
    try:
        session.query(History).filter(History.user_email == email).delete()
        session.commit()
    finally:
        session.close()