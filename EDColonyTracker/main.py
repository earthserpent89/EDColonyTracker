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
- toggle_completed(): Toggles the visibility of completed deliveries.
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

# Fetch available items from the database
def fetch_items():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM items")
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

# Fetch available construction sites from the database
def fetch_construction_sites():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM construction_sites")
    construction_sites = [row[0] for row in cursor.fetchall()]
    conn.close()
    return construction_sites

# Fetch deliveries for the selected construction site
def fetch_deliveries(construction_site):
    conn = sqlite3.connect(f"{construction_site}.db")
    cursor = conn.cursor()
    cursor.execute("SELECT commodity, amount_required, SUM(quantity), construction_site FROM deliveries GROUP BY commodity, construction_site")
    rows = cursor.fetchall()
    deliveries = []
    for row in rows:
        commodity, amount_required, total_delivered, construction_site = row
        amount_required = amount_required if amount_required is not None else 0
        total_delivered = total_delivered if total_delivered is not None else 0
        remaining_amount = amount_required - total_delivered
        deliveries.append((commodity, amount_required, remaining_amount, total_delivered, construction_site))
    conn.close()
    return deliveries

# Function to update deliveries list in the GUI
def update_deliveries_list(show_completed=False):
    construction_site = construction_site_var.get()
    if not construction_site:
        return

    deliveries_list.delete(*deliveries_list.get_children())
    for delivery in fetch_deliveries(construction_site):
        if not show_completed and delivery[2] <= 0:
            continue
        deliveries_list.insert("", "end", values=delivery)

    # Apply alternating row colors
    for i, item in enumerate(deliveries_list.get_children()):
        if i % 2 == 0:
            deliveries_list.item(item, tags=('evenrow',))
        else:
            deliveries_list.item(item, tags=('oddrow',))

# Function to add a delivery
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

    conn = sqlite3.connect(f"{construction_site}.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM deliveries WHERE commodity = ? AND construction_site = ?", (commodity, construction_site))
    result = cursor.fetchone()
    if result:
        new_quantity = (result[0] if result[0] is not None else 0) + quantity
        cursor.execute("UPDATE deliveries SET quantity = ? WHERE commodity = ? AND construction_site = ?", (new_quantity, commodity, construction_site))
    else:
        cursor.execute("INSERT INTO deliveries (commodity, quantity, construction_site) VALUES (?, ?, ?)", (commodity, quantity, construction_site))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Added {quantity} units of {commodity} to {construction_site}!")
    update_deliveries_list()

# Function to export deliveries to a CSV file
def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    construction_sites = fetch_construction_sites()
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Commodity", "Amount Required", "Remaining Amount", "Total Delivered", "Construction Site"])
        for site in construction_sites:
            for delivery in fetch_deliveries(site):
                writer.writerow(delivery)

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

    for delivery in deliveries:
        if len(delivery) != 3:
            continue  # Skip rows that don't have exactly 3 columns
        commodity, amount_required, construction_site = delivery
        if not commodity or not construction_site:
            continue  # Skip rows with missing required fields
        amount_required = int(amount_required) if amount_required else 0
        conn = sqlite3.connect(f"{construction_site}.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS deliveries (id INTEGER PRIMARY KEY, commodity TEXT, quantity INTEGER, construction_site TEXT, amount_required INTEGER, UNIQUE(commodity, construction_site))")
        cursor.execute("SELECT amount_required FROM deliveries WHERE commodity = ? AND construction_site = ?", (commodity, construction_site))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE deliveries SET amount_required = ? WHERE commodity = ? AND construction_site = ?", (amount_required, commodity, construction_site))
        else:
            cursor.execute("INSERT INTO deliveries (commodity, amount_required, construction_site) VALUES (?, ?, ?)", (commodity, amount_required, construction_site))
        conn.commit()
        conn.close()

    update_construction_site_dropdown()
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
            cursor.execute("INSERT OR IGNORE INTO construction_sites (name) VALUES (?)", (new_site,))
            conn.commit()
            conn.close()
            create_tables(f"{new_site}.db")  # Create tables in the new construction site database
            construction_site_listbox.insert(tk.END, new_site)
            new_site_var.set("")
            update_construction_site_dropdown()

    def remove_construction_site():
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if selected_site:
            conn = sqlite3.connect("cargo_tracker.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM construction_sites WHERE name = ?", (selected_site,))
            conn.commit()
            conn.close()
            os.remove(f"{selected_site}.db")
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
    construction_site = construction_site_var.get()
    if not construction_site:
        return

    response = messagebox.askyesno("Clear Deliveries", f"Are you sure you want to clear all deliveries for {construction_site}?")
    if response:
        conn = sqlite3.connect(f"{construction_site}.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM deliveries")
        conn.commit()
        conn.close()
        update_deliveries_list()
        messagebox.showinfo("Success", f"All deliveries for {construction_site} have been cleared.")

# Function to toggle the visibility of completed deliveries
def toggle_completed():
    global show_completed
    show_completed = not show_completed
    update_deliveries_list(show_completed)
    show_completed_button.config(text="Hide Completed" if show_completed else "Show Completed")

# Create the main application window
root = tk.Tk()
root.title("Elite Dangerous Cargo Tracker")
root.geometry("800x400")
root.minsize(800, 400)  # Set minimum window size

# Frame for the top row of inputs
top_frame = tk.Frame(root)
top_frame.pack(pady=10, fill=tk.X)

# Centering frame for the top row of inputs
top_center_frame = tk.Frame(top_frame)
top_center_frame.pack(anchor=tk.CENTER)

# Dropdown for selecting cargo item (dynamic)
tk.Label(top_center_frame, text="Select Item:").grid(row=0, column=0, padx=5, sticky=tk.W)
item_var = tk.StringVar()
item_dropdown = ttk.Combobox(top_center_frame, textvariable=item_var)
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
construction_site_var = tk.StringVar()  # Define construction_site_var
construction_site_dropdown = ttk.Combobox(top_center_frame, textvariable=construction_site_var)
construction_site_dropdown['values'] = fetch_construction_sites()
construction_site_dropdown.grid(row=0, column=3, padx=5, sticky=tk.EW)

# Entry field for quantity
tk.Label(top_center_frame, text="Enter Quantity:").grid(row=0, column=4, padx=5, sticky=tk.W)
quantity_var = tk.StringVar()
quantity_entry = tk.Entry(top_center_frame, textvariable=quantity_var)
quantity_entry.grid(row=0, column=5, padx=5, sticky=tk.EW)

# Button to add delivery
add_button = tk.Button(top_center_frame, text="Add Delivery", command=add_delivery, width=15)
add_button.grid(row=0, column=6, padx=10, sticky=tk.EW)

# Configure column weights for dynamic resizing
top_center_frame.columnconfigure(1, weight=1)
top_center_frame.columnconfigure(3, weight=1)
top_center_frame.columnconfigure(5, weight=1)
top_center_frame.columnconfigure(6, weight=1)

# Frame for the bottom row of buttons
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10, fill=tk.X)

# Centering frame for the bottom row of buttons
bottom_center_frame = tk.Frame(bottom_frame)
bottom_center_frame.pack(anchor=tk.CENTER)

# Button to export deliveries to CSV
export_button = tk.Button(bottom_center_frame, text="Export to CSV", command=export_to_csv, width=15)
export_button.grid(row=0, column=1, padx=5, sticky=tk.EW)

# Button to import deliveries from CSV
import_button = tk.Button(bottom_center_frame, text="Import from CSV", command=import_from_csv, width=15)
import_button.grid(row=0, column=2, padx=5, sticky=tk.EW)

# Button to open the construction site manager
edit_sites_button = tk.Button(bottom_center_frame, text="Edit Construction Sites", command=open_construction_site_manager, width=20)
edit_sites_button.grid(row=0, column=0, padx=10, sticky=tk.EW)

# Button to show/hide completed deliveries
show_completed_button = tk.Button(bottom_center_frame, text="Show Completed", command=toggle_completed, width=15)
show_completed_button.grid(row=0, column=3, padx=5, sticky=tk.EW)

# Button to clear the database
clear_db_button = tk.Button(bottom_center_frame, text="Clear Deliveries", command=clear_database, width=15)
clear_db_button.grid(row=0, column=4, padx=5, sticky=tk.EW)

# Configure column weights for dynamic resizing
bottom_center_frame.columnconfigure(0, weight=1)
bottom_center_frame.columnconfigure(1, weight=1)
bottom_center_frame.columnconfigure(2, weight=1)
bottom_center_frame.columnconfigure(3, weight=1)
bottom_center_frame.columnconfigure(4, weight=1)

# Table to display deliveries
tk.Label(root, text="Delivery History:").pack()
deliveries_list = ttk.Treeview(root, columns=("Commodity", "Amount Required", "Remaining Amount", "Total Delivered", "Construction Site"), show="headings")
deliveries_list.heading("Commodity", text="Commodity")
deliveries_list.heading("Amount Required", text="Amount Required")
deliveries_list.heading("Remaining Amount", text="Remaining Amount")
deliveries_list.heading("Total Delivered", text="Total Delivered")
deliveries_list.heading("Construction Site", text="Construction Site")

# Set minimum width for each column
deliveries_list.column("Commodity", minwidth=100, width=150)
deliveries_list.column("Amount Required", minwidth=100, width=150)
deliveries_list.column("Remaining Amount", minwidth=100, width=150)
deliveries_list.column("Total Delivered", minwidth=100, width=150)
deliveries_list.column("Construction Site", minwidth=100, width=150)

# Apply alternating row colors
deliveries_list.tag_configure('evenrow', background='lightgrey')
deliveries_list.tag_configure('oddrow', background='white')

deliveries_list.pack(fill="both", expand=True)

# Initialize the show_completed flag
show_completed = False

update_deliveries_list()  # Load existing data

# Run the GUI
root.mainloop()
