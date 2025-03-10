"""
This module provides functions to create and manage the SQLite database for tracking deliveries,
items, and construction sites.
"""

import sqlite3
import os
from utils import get_logger, BASE_DIR

# Get a logger for this module
logger = get_logger('Database')

# Define the database directory path
DB_DIR = os.path.join(BASE_DIR, "databases")

def ensure_db_directory_exists():
    """Ensure the database directory exists, creating it if necessary."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        logger.info(f"Created database directory: {DB_DIR}")

def get_db_path(db_name):
    """Get the full path for a database file and ensure the directory exists."""
    ensure_db_directory_exists()
    return os.path.join(DB_DIR, db_name)

def create_tables(db_name="cargo_tracker.db"):
    """Create necessary database tables if they don't exist."""
    logger.debug("create_tables function called")
    db_path = get_db_path(db_name)
    try:
        with sqlite3.connect(db_path) as conn:
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
                logger.info(f"Added commodity column to {db_name}")
            if 'amount_required' not in columns:
                cursor.execute("ALTER TABLE deliveries ADD COLUMN amount_required INTEGER")
                logger.info(f"Added amount_required column to {db_name}")

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
            logger.info(f"Database tables created/verified in {db_name}")
    except sqlite3.Error as e:
        logger.error(f"Database error in create_tables: {e}")

def add_item(item_name):
    """Add a new item to the items table."""
    try:
        db_path = get_db_path("cargo_tracker.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO items (name) VALUES (?)", (item_name,))
            if cursor.rowcount > 0:
                logger.debug(f"Added item: {item_name}")
    except sqlite3.Error as e:
        logger.error(f"Database error in add_item: {e}")

def add_construction_site(construction_site_name):
    """Add a new construction site to the construction sites table."""
    try:
        # Add to main database
        db_path = get_db_path("cargo_tracker.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO construction_sites (name) VALUES (?)", (construction_site_name,))
            if cursor.rowcount > 0:
                logger.info(f"Added construction site: {construction_site_name}")
        
        # Create a separate database for the construction site with required tables
        site_db_path = get_db_path(f"{construction_site_name}.db")
        with sqlite3.connect(site_db_path) as conn:
            cursor = conn.cursor()
            
            # Create deliveries table directly (not relying on create_tables)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deliveries (
                    id INTEGER PRIMARY KEY,
                    commodity TEXT,
                    quantity INTEGER DEFAULT 0,
                    construction_site TEXT,
                    amount_required INTEGER DEFAULT 0
                )
            ''')
            logger.info(f"Created deliveries table for {construction_site_name}")
            
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error in add_construction_site: {e}")
        return False

def populate_items():
    """Populate the items table with a predefined list of commodities."""
    try:
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
        logger.info(f"Populated items table with {len(commodities)} commodities")
    except Exception as e:
        logger.error(f"Error in populate_items: {e}")

def initialize_database():
    """Initialize the database tables and populate items."""
    try:
        create_tables()
        populate_items()
        logger.info("Database successfully initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def fetch_items():
    """Fetch all items from the database."""
    items = []
    try:
        db_path = get_db_path("cargo_tracker.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM items")
            items = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Fetched {len(items)} items from database")
    except sqlite3.Error as e:
        logger.error(f"Database error in fetch_items: {e}")
    return items

def fetch_construction_sites():
    """Fetch all construction sites from the database."""
    construction_sites = []
    try:
        db_path = get_db_path("cargo_tracker.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM construction_sites")
            construction_sites = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Fetched {len(construction_sites)} construction sites from database")
    except sqlite3.Error as e:
        logger.error(f"Database error in fetch_construction_sites: {e}")
    return construction_sites

def fetch_deliveries(construction_site):
    """Fetch deliveries for a specific construction site."""
    deliveries = []
    try:
        db_path = get_db_path(f"{construction_site}.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT commodity, amount_required, SUM(quantity) FROM deliveries GROUP BY commodity")
            rows = cursor.fetchall()
            
            for row in rows:
                commodity, amount_required, total_delivered = row
                amount_required = amount_required if amount_required is not None else 0
                total_delivered = total_delivered if total_delivered is not None else 0
                remaining_amount = amount_required - total_delivered
                deliveries.append((commodity, amount_required, remaining_amount, total_delivered))
        logger.debug(f"Fetched {len(deliveries)} deliveries for {construction_site}")
    except sqlite3.Error as e:
        logger.error(f"Database error in fetch_deliveries: {e}")
    return deliveries

def add_delivery(construction_site, commodity, quantity):
    """Add a delivery to the database for a specific construction site."""
    try:
        db_path = get_db_path(f"{construction_site}.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM deliveries WHERE commodity = ?", (commodity,))
            result = cursor.fetchone()
            if result:
                new_quantity = (result[0] if result[0] is not None else 0) + quantity
                cursor.execute("UPDATE deliveries SET quantity = ? WHERE commodity = ?", (new_quantity, commodity))
                logger.info(f"Updated delivery: {quantity} units of {commodity} to {construction_site}, new total: {new_quantity}")
            else:
                cursor.execute("INSERT INTO deliveries (commodity, quantity, construction_site) VALUES (?, ?, ?)", 
                              (commodity, quantity, construction_site))
                logger.info(f"Added new delivery: {quantity} units of {commodity} to {construction_site}")
    except sqlite3.Error as e:
        logger.error(f"Database error in add_delivery: {e}")

def remove_construction_site(construction_site):
    """Remove a construction site from the database."""
    # First remove from the main database
    try:
        db_path = get_db_path("cargo_tracker.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM construction_sites WHERE name = ?", (construction_site,))
            if cursor.rowcount > 0:
                logger.info(f"Removed construction site: {construction_site}")
    except sqlite3.Error as e:
        logger.error(f"Database error in remove_construction_site: {e}")
        return False
        
    # Then try to remove the file
    site_db_path = get_db_path(f"{construction_site}.db")
    if os.path.exists(site_db_path):
        try:
            # Try to close any connections to the file
            import gc
            gc.collect()  # Force garbage collection to release file handles
            
            # Try to delete the file
            os.remove(site_db_path)
            logger.info(f"Removed database file for {construction_site}")
            return True
        except OSError as e:
            # If deletion fails, log it but don't fail the operation
            logger.warning(f"Could not remove database file for {construction_site}: {e}")
            logger.warning("The file may be in use by another application and will need to be removed manually.")
            
            # Return True anyway since the site was removed from the main database
            return True
    return True

def clear_deliveries(construction_site):
    """Clear all deliveries for a specific construction site."""
    try:
        db_path = get_db_path(f"{construction_site}.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM deliveries")
            logger.info(f"Cleared all deliveries for {construction_site}")
    except sqlite3.Error as e:
        logger.error(f"Database error in clear_deliveries: {e}")

def import_from_csv_to_db(csv_data):
    """Import data from CSV into the database."""
    imported_count = 0
    try:
        for delivery in csv_data:
            if len(delivery) < 3:
                continue
            
            commodity, amount_required, construction_site = delivery[:3]
            if not commodity or not construction_site:
                continue
                
            amount_required = int(amount_required) if amount_required and amount_required.isdigit() else 0

            # Add construction site
            add_construction_site(construction_site)
            
            # Use the dedicated function to add the commodity requirement
            add_commodity_requirement(construction_site, commodity, amount_required)
            imported_count += 1
        
        logger.info(f"Successfully imported {imported_count} records from CSV")
    except Exception as e:
        logger.error(f"Error during CSV import: {e}")

def add_commodity_requirement(construction_site, commodity, amount_required):
    """Add a commodity requirement to a construction site."""
    try:
        db_path = get_db_path(f"{construction_site}.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if the commodity already exists
            cursor.execute("SELECT id FROM deliveries WHERE commodity = ?", (commodity,))
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                cursor.execute("UPDATE deliveries SET amount_required = ? WHERE commodity = ?", 
                             (amount_required, commodity))
                logger.info(f"Updated requirement: {amount_required} units of {commodity} for {construction_site}")
            else:
                # Create new record
                cursor.execute("INSERT INTO deliveries (commodity, quantity, construction_site, amount_required) VALUES (?, 0, ?, ?)", 
                              (commodity, construction_site, amount_required))
                logger.info(f"Added new requirement: {amount_required} units of {commodity} for {construction_site}")
    except sqlite3.Error as e:
        logger.error(f"Database error in add_commodity_requirement: {e}")

def update_commodity_requirements(construction_site, requirements_list):
    """Update all commodity requirements for a construction site."""
    try:
        for commodity, amount in requirements_list:
            add_commodity_requirement(construction_site, commodity, amount)
        logger.info(f"Updated {len(requirements_list)} commodity requirements for {construction_site}")
    except Exception as e:
        logger.error(f"Error in update_commodity_requirements: {e}")

def remove_commodity_requirement(construction_site, commodity):
    """Remove a commodity requirement from a construction site."""
    try:
        db_path = get_db_path(f"{construction_site}.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM deliveries WHERE commodity = ?", (commodity,))
            if cursor.rowcount > 0:
                logger.info(f"Removed requirement for {commodity} from {construction_site}")
    except sqlite3.Error as e:
        logger.error(f"Database error in remove_commodity_requirement: {e}")