import sqlite3


conn = sqlite3.connect('discord_logs.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    content TEXT,
    timestamp DATETIME NOT NULL,
    reply_to_id INTEGER,
    edited BOOLEAN,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (reply_to_id) REFERENCES messages(id)
)
""")

conn.commit()
conn.close()
print("SQLite table created successfully!")
