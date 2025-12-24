import sqlite3

conn = sqlite3.connect("socienta.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS visitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    visitor_name TEXT NOT NULL,
    purpose TEXT,
    visit_date TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Visitors table created successfully")
