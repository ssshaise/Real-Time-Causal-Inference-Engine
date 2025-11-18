# src/utils/auth_db.py
import sqlite3
import json
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
DB_PATH = "data/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password_hash TEXT, full_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, 
                  type TEXT, timestamp TEXT, inputs TEXT, results TEXT)''')
    conn.commit()
    conn.close()

def create_user(email, password, full_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        hashed_pw = pwd_context.hash(password)
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hashed_pw, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    
    if row:
        try:
            return pwd_context.verify(password, row[0])
        except Exception:
            return False
    return False

def save_history(email, analysis_type, inputs, results):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    inputs_json = json.dumps(inputs)
    results_json = json.dumps(results)
    
    c.execute("INSERT INTO history (user_email, type, timestamp, inputs, results) VALUES (?, ?, ?, ?, ?)",
              (email, analysis_type, timestamp, inputs_json, results_json))
    conn.commit()
    conn.close()

def get_history(email):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE user_email=? ORDER BY id DESC LIMIT 20", (email,))
    rows = c.fetchall()
    conn.close()
    
    
    return [
        {
            "id": r["id"],
            "type": r["type"],
            "timestamp": r["timestamp"],
            "inputs": json.loads(r["inputs"]),
            "results": json.loads(r["results"])
        } for r in rows
    ]
    
def delete_history(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_email=?", (email,))
    conn.commit()
    conn.close()

init_db()