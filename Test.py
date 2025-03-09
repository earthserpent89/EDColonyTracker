import sqlite3

def add_delivery(item, quantity, location):
    """Insert a new delivery into the database."""
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO deliveries (item, quantity, location) 
        VALUES (?, ?, ?)
    ''', (item, quantity, location))

    conn.commit()
    conn.close()
    print(f"Added delivery: {quantity} units of {item} to {location}")

def get_deliveries():
    """Retrieve all deliveries from the database."""
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM deliveries')
    rows = cursor.fetchall()

    conn.close()
    return rows

# Add test data
add_delivery("Tritium", 100, "Fleet Carrier")
add_delivery("Building Materials", 250, "Colony Site A")

# Fetch and print all deliveries
deliveries = get_deliveries()
print("\nAll Deliveries:")
for delivery in deliveries:
    print(delivery)
