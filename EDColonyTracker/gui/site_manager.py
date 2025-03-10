"""
UI components for managing construction sites.
"""

import tkinter as tk
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import fetch_construction_sites, add_construction_site, remove_construction_site

def open_construction_site_manager(parent, update_callback=None):
    """Open the construction site management window."""
    manager_window = tk.Toplevel(parent)
    manager_window.title("Manage Construction Sites")
    manager_window.geometry("300x300")

    tk.Label(manager_window, text="Construction Sites:").pack()

    construction_site_listbox = tk.Listbox(manager_window)
    construction_site_listbox.pack(fill=tk.BOTH, expand=True)

    for site in fetch_construction_sites():
        construction_site_listbox.insert(tk.END, site)

    def add_site():
        new_site = new_site_var.get()
        if new_site:
            add_construction_site(new_site)
            construction_site_listbox.insert(tk.END, new_site)
            new_site_var.set("")
            if update_callback:
                update_callback()

    def remove_site():
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if selected_site:
            remove_construction_site(selected_site)
            construction_site_listbox.delete(tk.ACTIVE)
            if update_callback:
                update_callback()

    new_site_var = tk.StringVar()
    tk.Entry(manager_window, textvariable=new_site_var).pack(fill=tk.X, padx=10, pady=5)
    tk.Button(manager_window, text="Add Construction Site", command=add_site).pack(fill=tk.X, padx=10, pady=5)
    tk.Button(manager_window, text="Remove Selected Site", command=remove_site).pack(fill=tk.X, padx=10, pady=5)