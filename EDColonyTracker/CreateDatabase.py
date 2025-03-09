import os
print("Current working directory:", os.getcwd())

import sqlite3

# Connect to the database (creates if it doesn't exist)
conn = sqlite3.connect("cargo_tracker.db")
cursor = conn.cursor()

# Create a table for tracking deliveries
cursor.execute('''
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    location TEXT NOT NULL
)
''')

# Commit and close
conn.commit()
conn.close()

print("Database setup complete!")
