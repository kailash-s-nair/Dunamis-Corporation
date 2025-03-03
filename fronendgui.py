import tkinter as tk
from tkinter import simpledialog

def add_item():
    item = simpledialog.askstring("Input", "Enter item name:")
    if item:
        listbox.insert(tk.END, item)

# Create main window
root = tk.Tk()
root.title("Item Adder")
root.geometry("300x300")

# Create Listbox
listbox = tk.Listbox(root)
listbox.pack(pady=20, fill=tk.BOTH, expand=True)

# Create Add button
add_button = tk.Button(root, text="Add Item", command=add_item)
add_button.pack(pady=10)

# Run the GUI loop
root.mainloop()
