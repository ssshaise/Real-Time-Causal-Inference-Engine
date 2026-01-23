import os
import json
from datetime import datetime
from passlib.context import CryptContext
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

# Password Hashing Setup
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)

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

def create_user(email, password, full_name):
    session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            return False
        
        # Hash password and save
        hashed_pw = pwd_context.hash(password)
        new_user = User(email=email, password_hash=hashed_pw, full_name=full_name)
        session.add(new_user)
        session.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_user(email, password):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return False
        return pwd_context.verify(password, user.password_hash)
    except Exception:
        return False
    finally:
        session.close()

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