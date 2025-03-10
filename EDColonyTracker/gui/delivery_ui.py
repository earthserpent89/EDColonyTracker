"""
UI components for managing and displaying deliveries.
"""

import tkinter as tk
from tkinter import ttk

def create_delivery_table(parent):
    """Create and return a treeview for displaying deliveries."""
    # Table to display deliveries
    tk.Label(parent, text="Delivery History:").pack()
    
    deliveries_list = ttk.Treeview(parent, 
                                  columns=("Commodity", "Amount Required", "Remaining Amount", "Total Delivered"),
                                  show="headings")
                                  
    deliveries_list.heading("Commodity", text="Commodity")
    deliveries_list.heading("Amount Required", text="Amount Required")
    deliveries_list.heading("Remaining Amount", text="Remaining Amount")
    deliveries_list.heading("Total Delivered", text="Total Delivered")

    # Set minimum width for each column
    deliveries_list.column("Commodity", minwidth=100, width=150)
    deliveries_list.column("Amount Required", minwidth=100, width=150)
    deliveries_list.column("Remaining Amount", minwidth=100, width=150)
    deliveries_list.column("Total Delivered", minwidth=100, width=150)

    # Apply alternating row colors
    deliveries_list.tag_configure('evenrow', background='lightgrey')
    deliveries_list.tag_configure('oddrow', background='white')

    deliveries_list.pack(fill="both", expand=True)
    
    return deliveries_list