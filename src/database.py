import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("survey_data.db")

def init_database():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sessions table - tracks each conversation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            status TEXT DEFAULT 'in_progress',
            zip_code TEXT,
            full_name TEXT,
            email TEXT,
            license_type TEXT,
            license_status TEXT
        )
    """)
    
    # Messages table - stores LIVE chat transcript
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            content TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    # Vehicles table - stores vehicle info
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            vehicle_identifier TEXT,
            vehicle_use TEXT,
            blind_spot_warning TEXT,
            commute_days_per_week INTEGER,
            commute_one_way_miles INTEGER,
            annual_mileage INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    # Survey data table - stores final JSON
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_data (
            session_id TEXT PRIMARY KEY,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_data TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    conn.commit()
    conn.close()

def create_session(session_id):
    """Create a new chat session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO sessions (session_id, started_at, status)
        VALUES (?, ?, 'in_progress')
    """, (session_id, datetime.now()))
    
    conn.commit()
    conn.close()

def save_message(session_id, role, content):
    """Save a message to the database in REAL-TIME"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO messages (session_id, timestamp, role, content)
        VALUES (?, ?, ?, ?)
    """, (session_id, datetime.now(), role, content))
    
    conn.commit()
    conn.close()

def update_session_data(session_id, data):
    """Update session with personal info as it's collected"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    personal = data.get('personal_info', {})
    license_info = data.get('license', {})
    
    cursor.execute("""
        UPDATE sessions
        SET zip_code = ?, full_name = ?, email = ?, 
            license_type = ?, license_status = ?
        WHERE session_id = ?
    """, (
        personal.get('zip_code'),
        personal.get('full_name'),
        personal.get('email'),
        license_info.get('type'),
        license_info.get('status'),
        session_id
    ))
    
    conn.commit()
    conn.close()

def complete_session(session_id, data):
    """Mark session as complete and save final data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Update session status
    cursor.execute("""
        UPDATE sessions
        SET status = 'completed', completed_at = ?
        WHERE session_id = ?
    """, (datetime.now(), session_id))
    
    # Save final survey data
    cursor.execute("""
        INSERT OR REPLACE INTO survey_data (session_id, completed_at, raw_data)
        VALUES (?, ?, ?)
    """, (session_id, datetime.now(), json.dumps(data)))
    
    # Save vehicles
    vehicles = data.get('vehicles', [])
    for vehicle in vehicles:
        cursor.execute("""
            INSERT INTO vehicles (
                session_id, vehicle_identifier, vehicle_use,
                blind_spot_warning, commute_days_per_week,
                commute_one_way_miles, annual_mileage
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            vehicle.get('vehicle_identifier'),
            vehicle.get('vehicle_use'),
            vehicle.get('blind_spot_warning'),
            vehicle.get('commute_days_per_week'),
            vehicle.get('commute_one_way_miles'),
            vehicle.get('annual_mileage')
        ))
    
    conn.commit()
    conn.close()

def get_live_chat_transcript(session_id):
    """Get the current chat transcript for a session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return messages

def get_all_sessions():
    """Get all chat sessions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT session_id, started_at, completed_at, status, 
               full_name, email, zip_code
        FROM sessions
        ORDER BY started_at DESC
    """)
    
    sessions = cursor.fetchall()
    conn.close()
    
    return sessions

def get_session_details(session_id):
    """Get full details of a session including transcript"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute("""
        SELECT * FROM sessions WHERE session_id = ?
    """, (session_id,))
    session = cursor.fetchone()
    
    # Get messages
    cursor.execute("""
        SELECT timestamp, role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))
    messages = cursor.fetchall()
    
    # Get final data if completed
    cursor.execute("""
        SELECT raw_data FROM survey_data WHERE session_id = ?
    """, (session_id,))
    final_data = cursor.fetchone()
    
    conn.close()
    
    return {
        'session': session,
        'messages': messages,
        'final_data': json.loads(final_data[0]) if final_data else None
    }