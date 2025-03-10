"""
Elite Dangerous Cargo Tracker - Main Application Entry Point

This application tracks cargo deliveries for construction sites in Elite Dangerous.
"""

import tkinter as tk
from database import initialize_database, fetch_construction_sites
from gui import MainWindow

def main():
    """Main entry point for the application."""
    # Initialize the database
    initialize_database()
    
    # Create the main application window
    root = tk.Tk()
    app = MainWindow(root)
    
    # Set the initial value of the construction site dropdown to the first available construction site
    construction_sites = fetch_construction_sites()
    if construction_sites:
        app.construction_site_var.set(construction_sites[0])
        app.update_deliveries_list()
    
    # Run the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
