import tkinter as tk
from tkinter import simpledialog

def add_item():
    manufacturer = simpledialog.askstring("Input", "Enter Manufacturer:")
    model = simpledialog.askstring("Input", "Enter Model:")
    price = simpledialog.askstring("Input", "Enter Price:")

    if manufacturer and model and price:
        listbox.insert(tk.END, f"Manufacturer: {manufacturer}")
        listbox.insert(tk.END, f"Model: {model}")
        listbox.insert(tk.END, f"Price: ${price}")
        listbox.insert(tk.END, "-" * 30)  # Separator

def delete_item():
    selected = listbox.curselection()
    if not selected:
        return  # No selection made

    index = selected[0]

    # Ensure we don't delete headers or separators
    if index <= 1 or "-" in listbox.get(index):
        return

    # Get the start of the entry
    entry_start = index - (index % 4)

    for _ in range(4):  # Remove the full entry
        listbox.delete(entry_start)

def edit_item():
    selected = listbox.curselection()
    if not selected:
        return  # No selection made

    index = selected[0]

    # Ensure it's not the header or separator
    if index <= 1 or "-" in listbox.get(index):
        return  

    selected_text = listbox.get(index)

    if "Manufacturer:" in selected_text:
        new_value = simpledialog.askstring("Edit Manufacturer", "Modify Manufacturer:", initialvalue=selected_text.replace("Manufacturer: ", "").strip())
        if new_value:
            listbox.delete(index)  # Remove old value
            listbox.insert(index, f"Manufacturer: {new_value}")  # Insert at same index

    elif "Model:" in selected_text:
        new_value = simpledialog.askstring("Edit Model", "Modify Model:", initialvalue=selected_text.replace("Model: ", "").strip())
        if new_value:
            listbox.delete(index)
            listbox.insert(index, f"Model: {new_value}")

    elif "Price:" in selected_text:
        new_value = simpledialog.askstring("Edit Price", "Modify Price:", initialvalue=selected_text.replace("Price: $", "").strip())
        if new_value:
            listbox.delete(index)
            listbox.insert(index, f"Price: ${new_value}")

# Create main window
root = tk.Tk()
root.title("Item Manager")
root.geometry("300x400")

# Create Frame for Listbox and Scrollbar
frame = tk.Frame(root)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Create Listbox with Scrollbar
scrollbar = tk.Scrollbar(frame)
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
scrollbar.config(command=listbox.yview)

listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Add Header Row
listbox.insert(tk.END, "   ITEM LIST   ")
listbox.insert(tk.END, "=" * 30)  # Header separator

# Create Buttons
add_button = tk.Button(root, text="Add Item", command=add_item)
delete_button = tk.Button(root, text="Delete Item", command=delete_item)
edit_button = tk.Button(root, text="Edit Item", command=edit_item)

add_button.pack(pady=5)
delete_button.pack(pady=5)
edit_button.pack(pady=5)

# Run the GUI loop
root.mainloop()
