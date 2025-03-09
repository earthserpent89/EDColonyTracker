import sqlite3
# This script creates a SQLite database for tracking deliveries, items, and locations.
# It includes functions to create tables, add items and locations, and populate the items table.

def create_tables():
    print("create_tables function called")
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()

    # Create table for deliveries if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY,
            item TEXT,
            quantity INTEGER,
            location TEXT
        )
    ''')

    # Create table for items if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')

    # Create table for locations if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

def add_item(item_name):
    print(f"add_item function called with item_name: {item_name}")
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO items (name) VALUES (?)", (item_name,))
    conn.commit()
    conn.close()

def add_location(location_name):
    print(f"add_location function called with location_name: {location_name}")
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO locations (name) VALUES (?)", (location_name,))
    conn.commit()
    conn.close()

def populate_items():
    print("populate_items function called")
    commodities = [
        "Advance Catalysers", "Agri-Medicines", "Aluminium", "Animal Meat", "Basic Medicines",
        "Battle Weapons", "Beer", "Bioreducing Lichen", "Biowaste", "Ceramic Composites",
        "CMM Composites", "Coffee", "Combat Stabilisers", "Computer Components", "Copper",
        "Crop Harvesters", "Emergency Power Cells", "Evacuation Shelter", "Fish", "Food Cartridges",
        "Fruit & Veg", "Geological Equipment", "Grain", "H.E. Suits", "Insulating Membranes",
        "Land Enrichment Systems", "Liquid Oxygen", "Liquor", "Medical Diag. Equip.",
        "Micro Controllers", "Military Grade Fabrics", "Muon Imager", "Non-Lethal Weapon",
        "Pesticides", "Polymers", "Power Generators", "Reactive Armour", "Resonating Separators",
        "Robotics", "Semiconductors", "Steel", "Structural Regulators", "Surface Stabilisers",
        "Survival Equipment", "Superconductors", "Tea", "Titanium", "Water", "Water Purifiers", "Wine"
    ]

    for commodity in commodities:
        add_item(commodity)

# Ensure the functions are accessible
if __name__ == "__main__":
    create_tables()
    populate_items()
