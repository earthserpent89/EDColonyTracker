"""
Main window for the Elite Dangerous Cargo Tracker application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (fetch_items, fetch_construction_sites, fetch_deliveries,
                     add_delivery, clear_deliveries)
from gui.site_manager import open_construction_site_manager
from gui.delivery_ui import create_delivery_table
from utils import get_logger

# Get a logger for this module
logger = get_logger('MainWindow')

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Elite Dangerous Cargo Tracker")
        self.root.geometry("800x400")
        self.root.minsize(800, 400)
        
        # Create variables
        self.item_var = tk.StringVar()
        self.construction_site_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.show_completed = False
        
        logger.info("Initializing main application window")
        self._create_ui()
        
    def _create_ui(self):
        # Create the top frame with input controls
        self._create_input_frame()
        
        # Create the bottom frame with action buttons
        self._create_button_frame()
        
        # Create the deliveries table
        self.deliveries_list = create_delivery_table(self.root)
        logger.debug("UI components created successfully")
        
    def _create_input_frame(self):
        # Frame for the top row of inputs
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill=tk.X)

        # Centering frame for the top row of inputs
        top_center_frame = tk.Frame(top_frame)
        top_center_frame.pack(anchor=tk.CENTER)

        # Dropdown for selecting cargo item (dynamic)
        tk.Label(top_center_frame, text="Select Item:").grid(row=0, column=0, padx=5, sticky=tk.W)
        item_dropdown = ttk.Combobox(top_center_frame, textvariable=self.item_var)
        item_dropdown['values'] = fetch_items()
        item_dropdown.grid(row=0, column=1, padx=5, sticky=tk.EW)

        # Enable autocomplete for the item dropdown
        def on_item_entry(event):
            value = event.widget.get()
            if value == '':
                item_dropdown['values'] = fetch_items()
            else:
                data = []
                for item in fetch_items():
                    if value.lower() in item.lower():
                        data.append(item)
                item_dropdown['values'] = data

        item_dropdown.bind('<KeyRelease>', on_item_entry)

        # Dropdown for selecting construction site (dynamic)
        tk.Label(top_center_frame, text="Select Construction Site:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.construction_site_dropdown = ttk.Combobox(top_center_frame, textvariable=self.construction_site_var)
        self.construction_site_dropdown['values'] = fetch_construction_sites()
        self.construction_site_dropdown.grid(row=0, column=3, padx=5, sticky=tk.EW)

        # Bind the event to update the deliveries list when a construction site is selected
        self.construction_site_dropdown.bind("<<ComboboxSelected>>", lambda event: self.update_deliveries_list())

        # Entry field for quantity
        tk.Label(top_center_frame, text="Enter Quantity:").grid(row=0, column=4, padx=5, sticky=tk.W)
        quantity_entry = tk.Entry(top_center_frame, textvariable=self.quantity_var)
        quantity_entry.grid(row=0, column=5, padx=5, sticky=tk.EW)

        # Button to add delivery
        add_button = tk.Button(top_center_frame, text="Add Delivery", command=self.add_delivery, width=15)
        add_button.grid(row=0, column=6, padx=10, sticky=tk.EW)

        # Configure column weights for dynamic resizing
        top_center_frame.columnconfigure(1, weight=1)
        top_center_frame.columnconfigure(3, weight=1)
        top_center_frame.columnconfigure(5, weight=1)
        top_center_frame.columnconfigure(6, weight=1)
        
    def _create_button_frame(self):
        # Frame for the bottom row of buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10, fill=tk.X)

        # Centering frame for the bottom row of buttons
        bottom_center_frame = tk.Frame(bottom_frame)
        bottom_center_frame.pack(anchor=tk.CENTER)

        # Button to export deliveries to CSV
        export_button = tk.Button(bottom_center_frame, text="Export to CSV", command=self.export_to_csv, width=15)
        export_button.grid(row=0, column=1, padx=5, sticky=tk.EW)

        # Button to import deliveries from CSV
        import_button = tk.Button(bottom_center_frame, text="Import from CSV", command=self.import_from_csv, width=15)
        import_button.grid(row=0, column=2, padx=5, sticky=tk.EW)

        # Button to open the construction site manager
        edit_sites_button = tk.Button(bottom_center_frame, text="Edit Construction Sites", 
                                     command=self.open_site_manager, width=20)
        edit_sites_button.grid(row=0, column=0, padx=10, sticky=tk.EW)

        # Button to show/hide completed deliveries
        self.show_completed_button = tk.Button(bottom_center_frame, text="Show Completed", 
                                              command=self.toggle_completed, width=15)
        self.show_completed_button.grid(row=0, column=3, padx=5, sticky=tk.EW)

        # Button to clear the database
        clear_db_button = tk.Button(bottom_center_frame, text="Clear Deliveries", 
                                   command=self.clear_database, width=15)
        clear_db_button.grid(row=0, column=4, padx=5, sticky=tk.EW)

        # Configure column weights for dynamic resizing
        bottom_center_frame.columnconfigure(0, weight=1)
        bottom_center_frame.columnconfigure(1, weight=1)
        bottom_center_frame.columnconfigure(2, weight=1)
        bottom_center_frame.columnconfigure(3, weight=1)
        bottom_center_frame.columnconfigure(4, weight=1)
        
    def update_deliveries_list(self, show_completed=None):
        """Update the deliveries list in the GUI."""
        if show_completed is None:
            show_completed = self.show_completed
            
        construction_site = self.construction_site_var.get()
        if not construction_site:
            return

        logger.debug(f"Updating deliveries list for {construction_site}")
        self.deliveries_list.delete(*self.deliveries_list.get_children())
        for delivery in fetch_deliveries(construction_site):
            if not show_completed and delivery[2] <= 0:
                continue
            remaining_amount = '✅' if delivery[2] <= 0 else delivery[2]
            self.deliveries_list.insert("", "end", values=(delivery[0], delivery[1], remaining_amount, delivery[3]))

        # Apply alternating row colors
        for i, item in enumerate(self.deliveries_list.get_children()):
            if i % 2 == 0:
                self.deliveries_list.item(item, tags=('evenrow',))
            else:
                self.deliveries_list.item(item, tags=('oddrow',))
                
    def add_delivery(self):
        """Add a delivery to the database."""
        commodity = self.item_var.get()
        quantity = self.quantity_var.get()
        construction_site = self.construction_site_var.get()

        if not commodity or not quantity or not construction_site:
            logger.warning("Attempted to add delivery with missing information")
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            quantity = int(quantity)  # Ensure quantity is a number
        except ValueError:
            logger.warning(f"Invalid quantity: '{quantity}' is not a number")
            messagebox.showerror("Error", "Quantity must be a number!")
            return

        logger.info(f"Adding delivery: {quantity} units of {commodity} to {construction_site}")
        add_delivery(construction_site, commodity, quantity)

        messagebox.showinfo("Success", f"Added {quantity} units of {commodity} to {construction_site}!")
        self.update_deliveries_list()
        
    def export_to_csv(self):
        """Export deliveries to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            logger.debug("Export to CSV cancelled by user")
            return

        logger.info(f"Exporting data to CSV: {file_path}")
        construction_sites = fetch_construction_sites()
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Commodity", "Amount Required", "Remaining Amount", "Total Delivered", "Construction Site"])
                rows_written = 0
                for site in construction_sites:
                    for delivery in fetch_deliveries(site):
                        remaining_amount = '✅' if delivery[2] <= 0 else delivery[2]
                        writer.writerow((delivery[0], delivery[1], remaining_amount, delivery[3], site))
                        rows_written += 1
                logger.info(f"Successfully exported {rows_written} rows of data")
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            messagebox.showerror("Error", f"Failed to export data: {e}")
        
    def import_from_csv(self):
        """Import deliveries from a CSV file."""
        from database import import_from_csv_to_db
        
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            logger.debug("Import from CSV cancelled by user")
            return

        try:
            logger.info(f"Importing data from CSV: {file_path}")
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                deliveries = [row for row in reader]

            import_from_csv_to_db(deliveries)
            self.update_construction_site_dropdown()
            self.update_deliveries_list()
            logger.info(f"Successfully imported {len(deliveries)} records from {file_path}")
            messagebox.showinfo("Success", f"Data imported from {file_path}")
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            messagebox.showerror("Error", f"Failed to import data: {e}")
        
    def open_site_manager(self):
        """Open the construction site manager."""
        logger.debug("Opening construction site manager")
        open_construction_site_manager(self.root, self.update_construction_site_dropdown)
        
    def update_construction_site_dropdown(self):
        """Update the construction site dropdown with fresh data."""
        logger.debug("Updating construction site dropdown")
        self.construction_site_dropdown['values'] = fetch_construction_sites()
        
    def toggle_completed(self):
        """Toggle the visibility of completed deliveries."""
        self.show_completed = not self.show_completed
        logger.debug(f"Toggled completed deliveries visibility to: {self.show_completed}")
        self.update_deliveries_list()
        self.show_completed_button.config(text="Hide Completed" if self.show_completed else "Show Completed")
        
    def clear_database(self):
        """Clear all deliveries for the selected construction site."""
        construction_site = self.construction_site_var.get()
        if not construction_site:
            logger.warning("Attempted to clear deliveries without selecting a construction site")
            return

        response = messagebox.askyesno("Clear Deliveries", 
                                      f"Are you sure you want to clear all deliveries for {construction_site}?")
        if response:
            logger.info(f"Clearing all deliveries for {construction_site}")
            clear_deliveries(construction_site)
            self.update_deliveries_list()
            messagebox.showinfo("Success", f"All deliveries for {construction_site} have been cleared.")
        else:
            logger.debug("Clear operation cancelled by user")