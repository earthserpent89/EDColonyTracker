"""
This script creates a SQLite database for tracking deliveries, items, and construction sites.
It includes functions to create tables, add items and construction sites, and populate the items table.
Functions:
    create_tables():
        Creates the necessary tables for deliveries, items, and construction sites if they do not exist.
        Adds new columns to the deliveries table if they do not exist.
    add_item(item_name: str):
        Adds a new item to the items table if it does not already exist.
        Args:
            item_name (str): The name of the item to add.
    add_construction_site(construction_site_name: str):
        Adds a new construction site to the construction sites table if it does not already exist.
        Args:
            construction_site_name (str): The name of the construction site to add.
    populate_items():
        Populates the items table with a predefined list of commodities.
"""

import sqlite3

def create_tables(db_name="cargo_tracker.db"):
    print("create_tables function called")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table for deliveries if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY,
            commodity TEXT,
            quantity INTEGER,
            construction_site TEXT,
            amount_required INTEGER,
            UNIQUE(commodity, construction_site)
        )
    ''')

    # Add new columns if they don't exist
    cursor.execute("PRAGMA table_info(deliveries)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'commodity' not in columns:
        cursor.execute("ALTER TABLE deliveries ADD COLUMN commodity TEXT")
    if 'amount_required' not in columns:
        cursor.execute("ALTER TABLE deliveries ADD COLUMN amount_required INTEGER")

    # Create table for items if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')

    # Create table for construction sites if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS construction_sites (
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

def add_construction_site(construction_site_name):
    print(f"add_construction_site function called with construction_site_name: {construction_site_name}")
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO construction_sites (name) VALUES (?)", (construction_site_name,))
    conn.commit()
    conn.close()

    # Create a separate database for the construction site
    create_tables(f"{construction_site_name}.db")

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
