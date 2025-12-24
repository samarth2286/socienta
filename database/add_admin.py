import sqlite3

conn = sqlite3.connect("socienta.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users (username, password, role)
VALUES (?, ?, ?)
""", ("admin", "admin123", "admin"))

conn.commit()
conn.close()

print("Admin user added successfully")
