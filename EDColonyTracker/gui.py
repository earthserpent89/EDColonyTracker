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

# Fetch available items and locations from the database
def fetch_items():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM items")
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

def fetch_locations():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM locations")
    locations = [row[0] for row in cursor.fetchall()]
    conn.close()
    return locations

# Existing function for adding a delivery
def add_delivery():
    item = item_var.get()
    quantity = quantity_var.get()
    location = location_var.get()

    if not item or not quantity or not location:
        messagebox.showerror("Error", "All fields must be filled!")
        return

    try:
        quantity = int(quantity)  # Ensure quantity is a number
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a number!")
        return

    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO deliveries (item, quantity, location) VALUES (?, ?, ?)", 
                   (item, quantity, location))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Added {quantity} units of {item} to {location}!")
    update_deliveries_list()

# Existing function for fetching all deliveries
def get_deliveries():
    conn = sqlite3.connect("cargo_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deliveries")
    rows = cursor.fetchall()
    conn.close()
    return rows

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
        writer.writerow(["ID", "Item", "Quantity", "Location"])
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
    cursor.executemany("INSERT INTO deliveries (id, item, quantity, location) VALUES (?, ?, ?, ?)", deliveries)
    conn.commit()
    conn.close()

    update_deliveries_list()
    messagebox.showinfo("Success", f"Data imported from {file_path}")

# Create the main application window
root = tk.Tk()
root.title("Elite Dangerous Cargo Tracker")
root.geometry("500x400")

# Dropdown for selecting cargo item (dynamic)
tk.Label(root, text="Select Item:").pack()
item_var = tk.StringVar()
item_dropdown = ttk.Combobox(root, textvariable=item_var)
item_dropdown['values'] = fetch_items()
item_dropdown.pack()

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

# Entry field for quantity
tk.Label(root, text="Enter Quantity:").pack()
quantity_var = tk.StringVar()
quantity_entry = tk.Entry(root, textvariable=quantity_var)
quantity_entry.pack()

# Dropdown for selecting delivery location (dynamic)
tk.Label(root, text="Select Location:").pack()
location_var = tk.StringVar()  # Define location_var
location_dropdown = ttk.Combobox(root, textvariable=location_var)
location_dropdown['values'] = fetch_locations()
location_dropdown.pack()

# Button to add delivery
add_button = tk.Button(root, text="Add Delivery", command=add_delivery)
add_button.pack(pady=10)

# Button to export deliveries to CSV
export_button = tk.Button(root, text="Export to CSV", command=export_to_csv)
export_button.pack(pady=5)

# Button to import deliveries from CSV
import_button = tk.Button(root, text="Import from CSV", command=import_from_csv)
import_button.pack(pady=5)

# Table to display deliveries
tk.Label(root, text="Delivery History:").pack()
deliveries_list = ttk.Treeview(root, columns=("ID", "Item", "Quantity", "Location"), show="headings")
deliveries_list.heading("ID", text="ID")
deliveries_list.heading("Item", text="Item")
deliveries_list.heading("Quantity", text="Quantity")
deliveries_list.heading("Location", text="Location")
deliveries_list.pack(fill="both", expand=True)

update_deliveries_list()  # Load existing data

# Run the GUI
root.mainloop()
