import sqlite3
import datetime
import os

# Database file name
DB_NAME = "smartcity_noc.db"

def get_connection():
    """Database connection establish karne ke liye helper function."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Tables create karne aur default admin banane ke liye."""
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # TABLE 1: ADMIN USERS
        c.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'System Admin'
            )
        ''')
        c.execute("INSERT OR IGNORE INTO admin_users (username, password) VALUES ('admin', 'admin123')")

        # TABLE 2: HELPDESK TICKETS
        c.execute('''
            CREATE TABLE IF NOT EXISTS helpdesk_tickets (
                ticket_id TEXT PRIMARY KEY,
                issue_type TEXT,
                priority TEXT,
                location TEXT,
                timestamp TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )
        ''')

        # TABLE 3: TRAFFIC LOGS
        c.execute('''
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER, 
                timestamp TEXT,
                cars INTEGER, 
                bikes INTEGER, 
                buses INTEGER, 
                trucks INTEGER,
                total_pcu REAL, 
                signal_state TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Smart City Database Initialized Successfully on Replit!")
    except Exception as e:
        print(f"❌ Database Init Error: {e}")

# --- TRAFFIC LOGGING ---
def log_traffic_data(node_id, counts, pcu, signal):
    try:
        conn = get_connection()
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cars = counts.get('car', 0)
        bikes = counts.get('motorbike', 0) + counts.get('bicycle', 0)
        buses = counts.get('bus', 0)
        trucks = counts.get('truck', 0)

        c.execute('''
            INSERT INTO traffic_logs 
            (node_id, timestamp, cars, bikes, buses, trucks, total_pcu, signal_state) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (node_id, now, cars, bikes, buses, trucks, pcu, signal))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Traffic DB Error: {e}")

# --- HELPDESK TICKETS ---
def add_ticket(ticket_id, issue_type, priority, location):
    try:
        conn = get_connection()
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''
            INSERT INTO helpdesk_tickets (ticket_id, issue_type, priority, location, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, issue_type, priority, location, now))
        
        conn.commit()
        conn.close()
        return now
    except Exception as e:
        print(f"❌ Ticket DB Error: {e}")

def get_active_tickets():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM helpdesk_tickets WHERE status='ACTIVE' ORDER BY timestamp DESC LIMIT 10")
        tickets = c.fetchall()
        conn.close()
        
        return [{
            "id": t["ticket_id"],
            "type": t["issue_type"],
            "priority": t["priority"],
            "location": t["location"],
            "time": t["timestamp"].split(" ")[1]
        } for t in tickets]
    except Exception as e:
        print(f"❌ Fetch Tickets Error: {e}")
        return []

# --- ADMIN LOGIN ---
def verify_login(username, password):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM admin_users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None
    except Exception as e:
        print(f"❌ Login DB Error: {e}")
        return False

# Replit trigger: Jab aap file run kareinge, tab database apne aap ban jayega
if __name__ == "__main__":
    init_db()