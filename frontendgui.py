import csv

# Read catalog from file
def read_catalog(file_name):
    catalog = []
    try:
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                catalog.append(row)
    except FileNotFoundError:
        print(f"{file_name} not found. Starting with an empty catalog.")
    return catalog

# Write catalog to file
def write_catalog(file_name, catalog):
    with open(file_name, mode='w', newline='') as file:
        fieldnames = catalog[0].keys() if catalog else ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(catalog)

# Display the menu
def menu():
    print("\nMenu")
    print("1. Add items")
    print("2. Delete items")
    print("3. Edit/Modify items")
    print("4. View dataset")
    print("5. Exit")
    choice = input("Select from one of the options: ")
    return choice

# Add an item
def add_item(catalog):
    new_length = input("sepal_length: ")
    new_width = input("sepal_width: ")
    description_length = input("petal_length: ")
    description_width = input("petal_width: ")
    species_add = input("species: ")
    catalog.append({"sepal_length": new_length, "sepal_width": new_width, "petal_length": description_length, "petal_width": description_width, "species": species_add})
    print("Item added successfully.")

# Delete an item by species
def delete_item(catalog):
    delete_species = input("Enter the species name to delete: ")
    for item in catalog:
        if item["species"].lower() == delete_species.lower():
            catalog.remove(item)
            print(f"Species '{delete_species}' deleted successfully.")
            return
    print(f"Species '{delete_species}' not found.")

# Edit an item by species
def edit_item(catalog):
    species_edit = input("Enter the species name to edit: ")
    for item in catalog:
        if item["species"].lower() == species_edit.lower():
            print("Leave blank to keep existing values.")
            item["sepal_length"] = input(f"New sepal_length ({item['sepal_length']}): ") or item["sepal_length"]
            item["sepal_width"] = input(f"New sepal_width ({item['sepal_width']}): ") or item["sepal_width"]
            item["petal_length"] = input(f"New petal_length ({item['petal_length']}): ") or item["petal_length"]
            item["petal_width"] = input(f"New petal_width ({item['petal_width']}): ") or item["petal_width"]
            print(f"Species '{species_edit}' updated successfully.")
            return
    print(f"Species '{species_edit}' not found.")

# View catalog
def view_catalog(catalog):
    if not catalog:
        print("Catalog is empty.")
    else:
        print("\nCatalog Items:")
        for item in catalog:
            print(", ".join(f"{key}: {value}" for key, value in item.items()))

# Main function
def main():
    file_name = "iris.csv"  # Make sure to use the correct file name here
    catalog = read_catalog(file_name)

    while True:
        choice = menu()
        if choice == '1':
            add_item(catalog)
        elif choice == '2':
            delete_item(catalog)
        elif choice == '3':
            edit_item(catalog)
        elif choice == '4':
            view_catalog(catalog)
        elif choice == '5':
            write_catalog(file_name, catalog)
            print("Changes saved. Exiting the catalog system. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

# Run the program
if __name__ == "__main__":
    main()