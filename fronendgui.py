import tkinter as tk
from tkinter import simpledialog

def add_item():
    item = simpledialog.askstring("Input", "Enter item name:")
    if item:
        listbox.insert(tk.END, item)

def delete_item():
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected[0])

def edit_item():
    selected = listbox.curselection()
    if selected:
        current_text = listbox.get(selected[0])
        new_text = simpledialog.askstring("Edit Item", "Modify item:", initialvalue=current_text)
        if new_text:
            listbox.delete(selected[0])
            listbox.insert(selected[0], new_text)

# Create main window
root = tk.Tk()
root.title("Item Manager")
root.geometry("300x300")

# Create Listbox
listbox = tk.Listbox(root)
listbox.pack(pady=20, fill=tk.BOTH, expand=True)

# Create Buttons
add_button = tk.Button(root, text="Add Item", command=add_item)
delete_button = tk.Button(root, text="Delete Item", command=delete_item)
edit_button = tk.Button(root, text="Edit Item", command=edit_item)

add_button.pack(pady=5)
delete_button.pack(pady=5)
edit_button.pack(pady=5)

# Run the GUI loop
root.mainloop()
