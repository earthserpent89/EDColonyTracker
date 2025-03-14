"""
UI components for managing construction sites and their commodity requirements.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (fetch_construction_sites, add_construction_site, 
                     remove_construction_site, fetch_items, fetch_deliveries,
                     update_commodity_requirements)
from utils import get_logger

# Get a logger for this module
logger = get_logger('SiteManager')

def open_construction_site_manager(parent, update_callback=None):
    """Open the construction site management window."""
    logger.info("Opening construction site manager window")
    manager_window = tk.Toplevel(parent)
    manager_window.title("Manage Construction Sites")
    manager_window.geometry("650x500")
    manager_window.minsize(650, 500)

    # Split the window into left and right frames
    left_frame = tk.Frame(manager_window, padx=10, pady=10)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    right_frame = tk.Frame(manager_window, padx=10, pady=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # --- LEFT SIDE: SITE MANAGEMENT ---
    tk.Label(left_frame, text="Construction Sites:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

    construction_site_listbox = tk.Listbox(left_frame, height=15)
    construction_site_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Add scrollbar to listbox
    scrollbar = tk.Scrollbar(construction_site_listbox)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    construction_site_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=construction_site_listbox.yview)

    # Populate with existing sites
    sites = fetch_construction_sites()
    logger.debug(f"Loaded {len(sites)} construction sites")
    for site in sites:
        construction_site_listbox.insert(tk.END, site)

    # Site entry and buttons frame
    site_entry_frame = tk.Frame(left_frame)
    site_entry_frame.pack(fill=tk.X, pady=5)
    
    new_site_var = tk.StringVar()
    tk.Label(site_entry_frame, text="Site Name:").pack(side=tk.LEFT)
    tk.Entry(site_entry_frame, textvariable=new_site_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def add_site():
        new_site = new_site_var.get()
        if not new_site:
            logger.warning("Attempted to add site with empty name")
            messagebox.showwarning("Input Required", "Please enter a site name")
            return
            
        logger.info(f"Adding new construction site: {new_site}")
        add_construction_site(new_site)
        construction_site_listbox.insert(tk.END, new_site)
        new_site_var.set("")
        if update_callback:
            update_callback()
    
    def remove_site():
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if not selected_site:
            logger.warning("Attempted to remove site without selecting one")
            messagebox.showwarning("Selection Required", "Please select a site to remove")
            return
            
        confirm = messagebox.askyesno("Confirm Deletion", 
                                      f"Are you sure you want to delete {selected_site}?\nThis will delete all delivery records for this site.")
        if confirm:
            logger.info(f"Removing construction site: {selected_site}")
            remove_construction_site(selected_site)
            construction_site_listbox.delete(tk.ACTIVE)
            if update_callback:
                update_callback()
        else:
            logger.debug(f"Canceled removal of site: {selected_site}")

    buttons_frame = tk.Frame(left_frame)
    buttons_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(buttons_frame, text="Add Site", command=add_site).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    tk.Button(buttons_frame, text="Remove Site", command=remove_site).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    # --- RIGHT SIDE: COMMODITY REQUIREMENTS ---
    tk.Label(right_frame, text="Commodity Requirements:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
    
    # Requirements listbox frame
    requirements_frame = tk.Frame(right_frame)
    requirements_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Commodity requirements listbox with headers
    columns = ("Commodity", "Amount Required")
    requirements_tree = ttk.Treeview(requirements_frame, columns=columns, show="headings", height=10)
    
    requirements_tree.heading("Commodity", text="Commodity")
    requirements_tree.heading("Amount Required", text="Amount Required")
    
    requirements_tree.column("Commodity", width=150)
    requirements_tree.column("Amount Required", width=100)
    
    requirements_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Add scrollbar to treeview
    tree_scrollbar = ttk.Scrollbar(requirements_frame, orient="vertical", command=requirements_tree.yview)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    requirements_tree.configure(yscrollcommand=tree_scrollbar.set)
    
    # Add commodity frame
    add_commodity_frame = tk.LabelFrame(right_frame, text="Add Commodity", padx=5, pady=5)
    add_commodity_frame.pack(fill=tk.X, pady=10)
    
    # Commodity dropdown
    tk.Label(add_commodity_frame, text="Commodity:").grid(row=0, column=0, sticky=tk.W)
    
    commodity_var = tk.StringVar()
    commodity_dropdown = ttk.Combobox(add_commodity_frame, textvariable=commodity_var)
    items = fetch_items()
    logger.debug(f"Loaded {len(items)} items for commodity dropdown")
    commodity_dropdown['values'] = items
    commodity_dropdown.grid(row=0, column=1, padx=5, sticky=tk.EW)
    
    # Enable autocomplete for commodity dropdown
    def on_commodity_entry(event):
        value = event.widget.get()
        if value == '':
            commodity_dropdown['values'] = fetch_items()
        else:
            data = []
            for item in fetch_items():
                if value.lower() in item.lower():
                    data.append(item)
            commodity_dropdown['values'] = data
            logger.debug(f"Filtered commodity dropdown to {len(data)} items matching '{value}'")

    commodity_dropdown.bind('<KeyRelease>', on_commodity_entry)
    
    # Amount required entry
    tk.Label(add_commodity_frame, text="Amount Required:").grid(row=0, column=2, padx=5, sticky=tk.W)
    amount_var = tk.StringVar()
    amount_entry = tk.Entry(add_commodity_frame, textvariable=amount_var, width=10)
    amount_entry.grid(row=0, column=3, padx=5, sticky=tk.W)
    
    add_commodity_frame.columnconfigure(1, weight=1)
    
    # Action buttons for commodity requirements
    def add_commodity_requirement_to_tree():
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if not selected_site:
            logger.warning("Attempted to add commodity without selecting a site")
            messagebox.showwarning("Selection Required", "Please select a construction site first")
            return
        
        commodity = commodity_var.get()
        amount = amount_var.get()
        
        if not commodity or not amount:
            logger.warning("Attempted to add commodity with missing information")
            messagebox.showwarning("Input Required", "Please select a commodity and enter an amount")
            return
            
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError as e:
            logger.warning(f"Invalid amount entered: {amount_var.get()}")
            messagebox.showerror("Invalid Input", "Please enter a positive number for the amount")
            return
        
        # Check if the commodity already exists in the treeview
        existing_item_id = None
        for item_id in requirements_tree.get_children():
            item = requirements_tree.item(item_id)
            if item['values'][0] == commodity:
                existing_item_id = item_id
                break
        
        if existing_item_id:
            # Update existing item
            logger.info(f"Updating commodity requirement: {commodity} to {amount} for {selected_site}")
            requirements_tree.item(existing_item_id, values=(commodity, amount))
        else:
            # Add new item
            logger.info(f"Adding new commodity requirement: {commodity} ({amount}) for {selected_site}")
            requirements_tree.insert("", tk.END, values=(commodity, amount))
        
        # Clear the entry fields
        commodity_var.set("")
        amount_var.set("")

    def remove_commodity_requirement_from_tree():
        selected_item = requirements_tree.selection()
        if not selected_item:
            logger.warning("Attempted to remove commodity without selecting one")
            messagebox.showwarning("Selection Required", "Please select a commodity to remove")
            return
            
        selected_values = requirements_tree.item(selected_item)['values']
        logger.info(f"Removing commodity requirement: {selected_values[0]}")
        requirements_tree.delete(selected_item)

    def save_all_requirements():
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if not selected_site:
            logger.warning("Attempted to save requirements without selecting a site")
            messagebox.showwarning("Selection Required", "Please select a construction site")
            return
            
        # Get all items from the treeview
        requirements = []
        for item_id in requirements_tree.get_children():
            item = requirements_tree.item(item_id)
            commodity, amount = item['values']
            requirements.append((commodity, int(amount)))
            
        if not requirements:
            logger.warning("Attempted to save empty requirements list")
            messagebox.showwarning("No Requirements", "Please add at least one commodity requirement")
            return
            
        # Save all requirements using the database function
        logger.info(f"Saving {len(requirements)} commodity requirements for {selected_site}")
        try:
            update_commodity_requirements(selected_site, requirements)
            messagebox.showinfo("Success", f"Requirements saved for {selected_site}")
            if update_callback:
                update_callback()
        except Exception as e:
            logger.error(f"Error saving requirements: {e}")
            messagebox.showerror("Error", f"Failed to save requirements: {e}")

    # When a site is selected, load its requirements
    def on_site_select(event):
        selected_site = construction_site_listbox.get(tk.ACTIVE)
        if selected_site:
            # Clear the requirements tree
            requirements_tree.delete(*requirements_tree.get_children())
            
            # Load requirements for the selected site
            logger.debug(f"Loading requirements for site: {selected_site}")
            try:
                deliveries = fetch_deliveries(selected_site)
                count = 0
                for delivery in deliveries:
                    commodity, amount_required, _, _ = delivery
                    if amount_required > 0:  # Only show items with requirements
                        requirements_tree.insert("", tk.END, values=(commodity, amount_required))
                        count += 1
                logger.debug(f"Loaded {count} requirements for {selected_site}")
            except Exception as e:
                logger.error(f"Error loading requirements for {selected_site}: {e}")

    construction_site_listbox.bind('<<ListboxSelect>>', on_site_select)
    
    # Add buttons for commodity management
    buttons_frame2 = tk.Frame(right_frame)
    buttons_frame2.pack(fill=tk.X, pady=5)
    
    tk.Button(buttons_frame2, text="Add Commodity", command=add_commodity_requirement_to_tree).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    tk.Button(buttons_frame2, text="Remove Commodity", command=remove_commodity_requirement_from_tree).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Save all button
    tk.Button(right_frame, text="Save All Requirements", command=save_all_requirements, 
             bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=10)
    
    logger.debug("Construction site manager UI setup complete")