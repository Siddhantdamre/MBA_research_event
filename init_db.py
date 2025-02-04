import sqlite3
from werkzeug.security import generate_password_hash

# Database file name
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Insert sample users
    users = [
        ("team1", generate_password_hash("team1pass"), "team"),
        ("team2", generate_password_hash("team2pass"), "team"),
        ("admin1", generate_password_hash("adminpass"), "admin")
    ]
    
    # Insert users into the table
    cursor.executemany('''
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', users)
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized and sample users added.")

def init_announcements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Table 'announcements' initialized.")

def init_proposals():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team TEXT NOT NULL,
            round INTEGER NOT NULL,
            proposal TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Table 'proposals' initialized.")

def add_mock_proposals():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO proposals (team, round, proposal) 
        VALUES (?, ?, ?)
    ''', [
        ("team1", 1, "Proposal for round 1"),
        ("team2", 1, "Proposal for round 1"),
        ("team1", 2, "Proposal for round 2")
    ])
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    init_announcements()
    init_proposals()
    app.run(debug=True)
