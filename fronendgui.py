import tkinter as tk
from tkinter import simpledialog

def add_item():
    manufacturer = simpledialog.askstring("Input", "Enter Manufacturer:")
    model = simpledialog.askstring("Input", "Enter Model:")
    price = simpledialog.askstring("Input", "Enter Price:")

    if manufacturer and model and price:
        listbox.insert(tk.END, f"{manufacturer:<15}| {model:<15}| ${price:<10}")
        listbox.insert(tk.END, "-" * 46)  # Row separator

def delete_item():
    selected = listbox.curselection()
    if selected and (selected[0] % 2 == 1):  # Ensure selecting a valid row
        index = selected[0] - 1  # Adjust to target actual row
        listbox.delete(index)  # Remove item row
        listbox.delete(index)  # Remove separator

def edit_item():
    selected = listbox.curselection()
    if selected and (selected[0] % 2 == 1):  # Ensure selecting an item row
        index = selected[0] - 1  # Adjust to target actual row
        row_data = listbox.get(index).split("|")

        if len(row_data) == 3:  # Ensure correct format
            manufacturer = row_data[0].strip()
            model = row_data[1].strip()
            price = row_data[2].strip().replace("$", "")

            new_manufacturer = simpledialog.askstring("Edit Item", "Modify Manufacturer:", initialvalue=manufacturer)
            new_model = simpledialog.askstring("Edit Item", "Modify Model:", initialvalue=model)
            new_price = simpledialog.askstring("Edit Item", "Modify Price:", initialvalue=price)

            if new_manufacturer and new_model and new_price:
                listbox.delete(index, index + 1)  # Remove old row and separator
                listbox.insert(index, f"{new_manufacturer:<15}| {new_model:<15}| ${new_price:<10}")
                listbox.insert(index + 1, "-" * 46)

# Create main window
root = tk.Tk()
root.title("Item Manager")
root.geometry("420x300")

# Create Frame for Listbox and Scrollbar
frame = tk.Frame(root)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Create Listbox with Scrollbar
scrollbar = tk.Scrollbar(frame)
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
scrollbar.config(command=listbox.yview)

listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Add Header Row
listbox.insert(tk.END, f"{'Manufacturer':<15}| {'Model':<15}| {'Price':<10}")
listbox.insert(tk.END, "=" * 46)  # Header separator

# Create Buttons
add_button = tk.Button(root, text="Add Item", command=add_item)
delete_button = tk.Button(root, text="Delete Item", command=delete_item)
edit_button = tk.Button(root, text="Edit Item", command=edit_item)

add_button.pack(pady=5)
delete_button.pack(pady=5)
edit_button.pack(pady=5)

# Run the GUI loop
root.mainloop()
