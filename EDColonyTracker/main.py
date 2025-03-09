"""
This module provides a graphical user interface (GUI) for tracking cargo deliveries in the game Elite Dangerous.
It includes functionalities for adding deliveries, managing construction sites, and importing/exporting data to/from CSV files.
Functions:
- initialize_database(): Ensures the database tables are created and items are populated.
- fetch_items(): Fetches available items from the database.
- fetch_construction_sites(): Fetches available construction sites from the database.
- add_delivery(): Adds a delivery to the database.
- get_deliveries(): Fetches all deliveries from the database.
- update_deliveries_list(): Updates the deliveries list in the GUI.
- export_to_csv(): Exports deliveries to a CSV file.
- import_from_csv(): Imports deliveries from a CSV file.
- open_construction_site_manager(): Opens the construction site management window.
- update_construction_site_dropdown(): Updates the construction site dropdown in the GUI.
- clear_database(): Clears all deliveries from the database.
GUI Components:
- Main application window with dropdowns for selecting items and construction sites, an entry field for quantity, and buttons for adding deliveries, exporting/importing data, managing construction sites, and clearing the database.
- A table to display the delivery history.
"""

# Import necessary libraries
import sys
import os
import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Ensure the CreateDatabase module is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from CreateDatabase import create_tables, populate_items

# Ensure the database tables are created and items are populated
def initialize_database():
    create_tables()
    populate_items()

# Initialize the database
initialize_database()

# Fetch available items and construction sites from the database
def fetch_items():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM items")
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

def fetch_construction_sites():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM locations")
    construction_sites = [row[0] for row in cursor.fetchall()]
    conn.close()
    return construction_sites

# Existing function for adding a delivery
def add_delivery():
    commodity = item_var.get()
    quantity = quantity_var.get()
    construction_site = construction_site_var.get()

    if not commodity or not quantity or not construction_site:
        messagebox.showerror("Error", "All fields must be filled!")
        return

    try:
        quantity = int(quantity)  # Ensure quantity is a number
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a number!")
        return

    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM deliveries WHERE commodity = ? AND location = ?", (commodity, construction_site))
    result = cursor.fetchone()
    if result:
        new_quantity = result[0] + quantity
        cursor.execute("UPDATE deliveries SET quantity = ? WHERE commodity = ? AND location = ?", (new_quantity, commodity, construction_site))
    else:
        cursor.execute("INSERT INTO deliveries (commodity, quantity, location) VALUES (?, ?, ?)", (commodity, quantity, construction_site))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Added {quantity} units of {commodity} to {construction_site}!")
    update_deliveries_list()

# Existing function for fetching all deliveries
def get_deliveries():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT commodity, amount_required, SUM(quantity), location FROM deliveries GROUP BY commodity, location")
    rows = cursor.fetchall()
    deliveries = []
    for row in rows:
        commodity, amount_required, total_delivered, location = row
        amount_required = amount_required if amount_required is not None else 0
        total_delivered = total_delivered if total_delivered is not None else 0
        remaining_amount = amount_required - total_delivered
        deliveries.append((commodity, amount_required, remaining_amount, total_delivered, location))
    conn.close()
    return deliveries

# Function to update deliveries list in the GUI
def update_deliveries_list():
    deliveries_list.delete(*deliveries_list.get_children())
    for delivery in get_deliveries():
        deliveries_list.insert("", "end", values=delivery)

# Function to export deliveries to a CSV file
def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    deliveries = get_deliveries()
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Commodity", "Amount Required", "Remaining Amount", "Total Delivered", "Construction Site"])
        writer.writerows(deliveries)

    messagebox.showinfo("Success", f"Data exported to {file_path}")

# Function to import deliveries from a CSV file
def import_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        deliveries = [row for row in reader]

    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    for delivery in deliveries:
        commodity, amount_required, location = delivery
        if not commodity or not location:
            continue  # Skip rows with missing required fields
        amount_required = int(amount_required) if amount_required else 0
        cursor.execute("SELECT amount_required FROM deliveries WHERE commodity = ? AND location = ?", (commodity, location))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE deliveries SET amount_required = ? WHERE commodity = ? AND location = ?", (amount_required, commodity, location))
        else:
            cursor.execute("INSERT INTO deliveries (commodity, amount_required, location) VALUES (?, ?, ?)", (commodity, amount_required, location))
    conn.commit()
    conn.close()

    update_deliveries_list()
    messagebox.showinfo("Success", f"Data imported from {file_path}")

# Function to open the construction site management window
def open_construction_site_manager():
    manager_window = tk.Toplevel(root)
    manager_window.title("Manage Construction Sites")
    manager_window.geometry("300x300")

    tk.Label(manager_window, text="Construction Sites:").pack()

    construction_site_listbox = tk.Listbox(manager_window)
    construction_site_listbox.pack(fill=tk.BOTH, expand=True)

    for site in fetch_construction_sites():
        construction_site_listbox.insert(tk.END, site)

    def add_construction_site():
        new_site = new_site_var.get()
        if new_site:
            conn = sqlite3.connect("cargo_tracker.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO locations (name) VALUES (?)", (new_site,))
            conn.commit()
            conn.close()
            construction_site_listbox.insert(tk.END, new_site)
            new_site_var.set("")
            update_construction_site_dropdown()

    def remove_construction_site():
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if selected_site:
            conn = sqlite3.connect("cargo_tracker.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM locations WHERE name = ?", (selected_site,))
            conn.commit()
            conn.close()
            construction_site_listbox.delete(tk.ACTIVE)
            update_construction_site_dropdown()

    new_site_var = tk.StringVar()
    tk.Entry(manager_window, textvariable=new_site_var).pack()
    tk.Button(manager_window, text="Add Construction Site", command=add_construction_site).pack()
    tk.Button(manager_window, text="Remove Selected Site", command=remove_construction_site).pack()

# Function to update the construction site dropdown
def update_construction_site_dropdown():
    construction_site_dropdown['values'] = fetch_construction_sites()

# Function to clear the database
def clear_database():
    response = messagebox.askyesno("Clear Deliveries", "Are you sure you want to clear all deliveries?")
    if response:
        conn = sqlite3.connect("cargo_tracker.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM deliveries")
        conn.commit()
        conn.close()
        update_deliveries_list()
        messagebox.showinfo("Success", "All deliveries have been cleared.")

# Create the main application window
root = tk.Tk()
root.title("Elite Dangerous Cargo Tracker")
root.geometry("600x400")

# Frame for the top row of inputs
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

# Dropdown for selecting cargo item (dynamic)
tk.Label(top_frame, text="Select Item:").grid(row=0, column=0, padx=5)
item_var = tk.StringVar()
item_dropdown = ttk.Combobox(top_frame, textvariable=item_var)
item_dropdown['values'] = fetch_items()
item_dropdown.grid(row=0, column=1, padx=5)

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
tk.Label(top_frame, text="Select Construction Site:").grid(row=0, column=2, padx=5)
construction_site_var = tk.StringVar()  # Define construction_site_var
construction_site_dropdown = ttk.Combobox(top_frame, textvariable=construction_site_var)
construction_site_dropdown['values'] = fetch_construction_sites()
construction_site_dropdown.grid(row=0, column=3, padx=5)

# Entry field for quantity
tk.Label(top_frame, text="Enter Quantity:").grid(row=0, column=4, padx=5)
quantity_var = tk.StringVar()
quantity_entry = tk.Entry(top_frame, textvariable=quantity_var)
quantity_entry.grid(row=0, column=5, padx=5)

# Button to add delivery
add_button = tk.Button(top_frame, text="Add Delivery", command=add_delivery)
add_button.grid(row=0, column=6, padx=5)

# Frame for the bottom row of buttons
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10)

# Button to export deliveries to CSV
export_button = tk.Button(bottom_frame, text="Export to CSV", command=export_to_csv)
export_button.grid(row=0, column=1, padx=5)

# Button to import deliveries from CSV
import_button = tk.Button(bottom_frame, text="Import from CSV", command=import_from_csv)
import_button.grid(row=0, column=2, padx=5)

# Button to open the construction site manager
edit_sites_button = tk.Button(bottom_frame, text="Edit Construction Sites", command=open_construction_site_manager)
edit_sites_button.grid(row=0, column=0, padx=5)

# Button to clear the database
clear_db_button = tk.Button(bottom_frame, text="Clear Deliveries", command=clear_database)
clear_db_button.grid(row=0, column=3, padx=5)

# Table to display deliveries
tk.Label(root, text="Delivery History:").pack()
deliveries_list = ttk.Treeview(root, columns=("Commodity", "Amount Required", "Remaining Amount", "Total Delivered", "Construction Site"), show="headings")
deliveries_list.heading("Commodity", text="Commodity")
deliveries_list.heading("Amount Required", text="Amount Required")
deliveries_list.heading("Remaining Amount", text="Remaining Amount")
deliveries_list.heading("Total Delivered", text="Total Delivered")
deliveries_list.heading("Construction Site", text="Construction Site")
deliveries_list.pack(fill="both", expand=True)

update_deliveries_list()  # Load existing data

# Run the GUI
root.mainloop()
