import tkinter as tk
from tkinter import simpledialog, Menu

def add_item():
    manufacturer = simpledialog.askstring("Input", "Enter Manufacturer:")
    model = simpledialog.askstring("Input", "Enter Model:")
    
    while True:
        price = simpledialog.askstring("Input", "Enter Price (Numbers Only):")
        if price and price.replace('.', '', 1).isdigit():  # Ensures numeric input
            price = float(price)
            break
        else:
            tk.messagebox.showerror("Invalid Input", "Please enter a valid numeric price.")

    if manufacturer and model and price:
        entry = {
            "manufacturer": manufacturer,
            "model": model,
            "price": price,
            "favorite": False
        }
        item_list.append(entry)
        update_listbox()

def delete_item():
    selected = listbox.curselection()
    if not selected:
        return

    selected_text = listbox.get(selected[0])
    for item in item_list:
        if item["manufacturer"] in selected_text:
            item_list.remove(item)
            break
    
    update_listbox()

def edit_item():
    selected = listbox.curselection()
    if not selected:
        return
    
    selected_text = listbox.get(selected[0])
    for item in item_list:
        if item["manufacturer"] in selected_text:
            manufacturer = simpledialog.askstring("Edit Manufacturer", "Modify Manufacturer:", initialvalue=item["manufacturer"])
            model = simpledialog.askstring("Edit Model", "Modify Model:", initialvalue=item["model"])
            
            while True:
                price = simpledialog.askstring("Edit Price", "Modify Price:", initialvalue=str(item["price"]))
                if price and price.replace('.', '', 1).isdigit():
                    price = float(price)
                    break
                else:
                    tk.messagebox.showerror("Invalid Input", "Please enter a valid numeric price.")
            
            if manufacturer and model and price:
                item["manufacturer"] = manufacturer
                item["model"] = model
                item["price"] = price
            break
    
    update_listbox()

def toggle_favorite():
    selected = listbox.curselection()
    if not selected:
        return
    
    selected_text = listbox.get(selected[0])
    for item in item_list:
        if item["manufacturer"] in selected_text:
            item["favorite"] = not item["favorite"]
            break
    
    update_listbox()

def sort_items(criteria):
    global item_list, sort_criterion
    sort_criterion = criteria
    update_listbox()

def show_sort_menu():
    sort_menu = Menu(root, tearoff=0)
    sort_menu.add_command(label="By Manufacturer", command=lambda: sort_items("manufacturer"))
    sort_menu.add_command(label="By Model", command=lambda: sort_items("model"))
    sort_menu.add_command(label="By Price", command=lambda: sort_items("price"))
    sort_menu.post(sort_button.winfo_rootx(), sort_button.winfo_rooty() + sort_button.winfo_height())

def update_listbox():
    listbox.delete(2, tk.END)  # Keep headers, clear the rest
    
    if sort_criterion == "manufacturer":
        sorted_items = sorted(item_list, key=lambda x: (not x["favorite"], x["manufacturer"].lower()))
    elif sort_criterion == "model":
        sorted_items = sorted(item_list, key=lambda x: (not x["favorite"], x["model"].lower()))
    elif sort_criterion == "price":
        sorted_items = sorted(item_list, key=lambda x: (not x["favorite"], -x["price"]))
    else:
        sorted_items = sorted(item_list, key=lambda x: (not x["favorite"], x["manufacturer"].lower()))
    
    for item in sorted_items:
        fav_marker = "★ " if item["favorite"] else ""
        listbox.insert(tk.END, f"{fav_marker}{item['manufacturer']}  |  {item['model']}  |  ${item['price']:.2f}")

# Create main window
root = tk.Tk()
root.title("Item Manager")
root.geometry("400x450")

# Create Listbox
frame = tk.Frame(root)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
scrollbar.config(command=listbox.yview)

listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Header
listbox.insert(tk.END, "   Manufacturer  |  Model  |  Price   ")
listbox.insert(tk.END, "=" * 40)

# Data storage
item_list = []
sort_criterion = "manufacturer"  # Default sorting

# Buttons
add_button = tk.Button(root, text="Add Item", command=add_item)
delete_button = tk.Button(root, text="Delete Item", command=delete_item)
edit_button = tk.Button(root, text="Edit Item", command=edit_item)
favorite_button = tk.Button(root, text="Toggle Favorite", command=toggle_favorite)
sort_button = tk.Button(root, text="Sort by", command=show_sort_menu)

add_button.pack(pady=5)
delete_button.pack(pady=5)
edit_button.pack(pady=5)
favorite_button.pack(pady=5)
sort_button.pack(pady=5)

root.mainloop()
