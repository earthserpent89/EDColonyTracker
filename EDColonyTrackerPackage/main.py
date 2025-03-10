"""
Elite Dangerous Cargo Tracker - Main Application Entry Point

This application tracks cargo deliveries for construction sites in Elite Dangerous.
"""

import tkinter as tk
import sys
from database import initialize_database, fetch_construction_sites
from gui.main_window import MainWindow
from utils import get_logger

# Get a logger for the main module
logger = get_logger('Main')

def main():
    """Main entry point for the application."""
    try:
        logger.info("Starting EDColonyTracker application")
        
        # Initialize the database
        initialize_database()
        
        # Create the main application window
        root = tk.Tk()
        root.title("Elite Dangerous Colony Tracker")
        
        # Set application icon if available
        try:
            root.iconbitmap("resources/icon.ico")
        except Exception as e:
            logger.warning(f"Could not load application icon: {e}")
        
        app = MainWindow(root)
        
        # Set the initial value of the construction site dropdown to the first available construction site
        construction_sites = fetch_construction_sites()
        if construction_sites:
            logger.info(f"Found {len(construction_sites)} existing construction sites")
            app.construction_site_var.set(construction_sites[0])
            app.update_deliveries_list()
        else:
            logger.info("No existing construction sites found")
        
        logger.info("Application initialized, starting main loop")
        
        # Run the GUI
        root.mainloop()
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        # Show error in GUI if possible, otherwise use console
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", f"An unexpected error occurred: {e}")
        except:
            print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
