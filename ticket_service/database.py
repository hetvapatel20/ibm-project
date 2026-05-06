from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 💻 LOCAL & CLOUD DB SETUP
# ==========================================
LOCAL_DB_URL = "sqlite:///./smartcity_noc.db"
engine_local = create_engine(LOCAL_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_local)

Base = declarative_base() 

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

SUPABASE_URL = "postgresql://postgres:Nisarg%407112@db.uqtxstbrrefczknnotmc.supabase.co:6543/postgres?sslmode=require"
try: engine_supabase = create_engine(SUPABASE_URL, connect_args={"connect_timeout": 5})
except Exception as e: engine_supabase = None

NEON_URL = "postgresql://neondb_owner:npg_H9hNoDpn3Qrl@ep-purple-rice-ambmhzcg.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
try: engine_neon = create_engine(NEON_URL, connect_args={"connect_timeout": 5})
except Exception as e: engine_neon = None

def init_db():
    try: Base.metadata.create_all(bind=engine_local)
    except: pass
    if engine_supabase:
        try: Base.metadata.create_all(bind=engine_supabase)
        except: pass
    if engine_neon:
        try: Base.metadata.create_all(bind=engine_neon)
        except: pass

    try:
        conn = sqlite3.connect("smartcity_noc.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'System Admin')''')
        c.execute("INSERT OR IGNORE INTO admin_users (username, password) VALUES ('admin', 'admin123')")
        c.execute('''CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INTEGER, timestamp TEXT, cars INTEGER, bikes INTEGER, buses INTEGER, trucks INTEGER, total_pcu REAL, signal_state TEXT)''')
        
        # 🔥 NAYI AUDIT LOGS TABLE 🔥
        c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, admin_name TEXT, action TEXT, details TEXT, timestamp TEXT)''')
        
        conn.commit()
        conn.close()
        print("✅ Database & Tables Initialized Successfully!")
    except: pass

def get_connection():
    conn = sqlite3.connect("smartcity_noc.db")
    conn.row_factory = sqlite3.Row
    return conn

def log_traffic_data(node_id, counts, pcu, signal):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cars = counts.get('car', 0)
    bikes = counts.get('motorbike', 0) + counts.get('bicycle', 0)
    buses = counts.get('bus', 0)
    trucks = counts.get('truck', 0)
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        c = conn.cursor()
        c.execute('''INSERT INTO traffic_logs (node_id, timestamp, cars, bikes, buses, trucks, total_pcu, signal_state) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (node_id, now, cars, bikes, buses, trucks, pcu, signal))
        conn.commit()
        conn.close()
    except: pass

def add_ticket(ticket_id_str, issue_type, priority, location):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        c = conn.cursor()
        c.execute('''INSERT INTO tickets (issue_type, location, device_id, severity, status, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)''', (issue_type, location, "DASHBOARD-001", priority, "open", now))
        conn.commit()
        conn.close()
    except: pass

    if engine_supabase:
        try:
            with engine_supabase.begin() as conn:
                conn.execute(text('''INSERT INTO tickets (issue_type, location, device_id, severity, status, created_at)
                                     VALUES (:typ, :loc, :dev, :sev, :stat, :time)'''), 
                             {"typ": issue_type, "loc": location, "dev": "DASHBOARD-001", "sev": priority, "stat": "open", "time": now})
        except: pass

    if engine_neon:
        try:
            with engine_neon.begin() as conn:
                conn.execute(text('''INSERT INTO tickets (issue_type, location, device_id, severity, status, created_at)
                                     VALUES (:typ, :loc, :dev, :sev, :stat, :time)'''), 
                             {"typ": issue_type, "loc": location, "dev": "DASHBOARD-001", "sev": priority, "stat": "open", "time": now})
        except: pass

def get_active_tickets():
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tickets WHERE status='open' OR status='in_progress' ORDER BY created_at DESC LIMIT 10")
        tickets = c.fetchall()
        conn.close()
        
        result = []
        for t in tickets:
            result.append({
                "id": str(t["ticket_id"]),
                "type": t["issue_type"],
                "priority": t["severity"],
                "location": t["location"],
                "time": str(t["created_at"]).split(" ")[1] if " " in str(t["created_at"]) else t["created_at"]
            })
        return result
    except: return []

def verify_login(username, password):
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        conn.row_factory = sqlite3.Row 
        c = conn.cursor()
        c.execute("SELECT * FROM admin_users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user: return {"username": user["username"], "role": user["role"]}
        return None
    except: return None

def create_new_user(username, password, role):
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        c = conn.cursor()
        c.execute("INSERT INTO admin_users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return True, f"Account '{username}' created as {role}!"
    except sqlite3.IntegrityError: return False, "Error: Username already exists!"
    except Exception as e: return False, f"Database Error: {e}"

def get_all_users():
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT username FROM admin_users")
        users = c.fetchall()
        conn.close()
        return [u["username"].lower() for u in users]
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

# 🔥 THE SECURE DELETE AND LOG FUNCTION 🔥
def delete_ticket_with_log(ticket_id, admin_username, issue_type, location):
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Log Generate Karo (Immutable Record)
        details = f"Deleted Ticket #{ticket_id}: {issue_type} at {location}"
        c.execute("INSERT INTO audit_logs (admin_name, action, details, timestamp) VALUES (?, ?, ?, ?)",
                  (admin_username, "DELETE", details, now))
        
        # 2. Local fallback deletion (Agar database mein hai)
        c.execute("DELETE FROM tickets WHERE ticket_id=?", (ticket_id,))
        
        conn.commit()
        conn.close()
        return True, "Ticket deleted and logged safely."
    except Exception as e:
        return False, str(e)

# 🔥 FETCH AUDIT LOGS 🔥
def get_audit_logs():
    try:
        conn = sqlite3.connect("smartcity_noc.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50")
        logs = c.fetchall()
        conn.close()
        return [dict(l) for l in logs]
    except: return []