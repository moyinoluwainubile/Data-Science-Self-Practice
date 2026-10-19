#empty inventory
inventories = {}

while True:
    print("\n--- INVENTORY MENU ---")
    print("1. Add Inventory")
    print("2. Remove Inventory")
    print("3. Update an Inventory")
    print("4. Show All Inventories")
    print("5. Quit")

    choice = input("Choose an option (1-5): ")
# add inventory section
    if choice == "1":
        try:
            inventory_id = input("Enter the Inventory ID: ").strip().lower()
            quantity = int(input("Enter Inventory Quantity: "))
            price = float(input("Enter Inventory Price: "))
            inventories[inventory_id] = {
                "quantity": quantity,
                "price": price
            }
            print(f"{inventory_id} has been added successfully!")
        except ValueError:
            print("Invalid Quantity or Price; please enter correct details where applicable!")
# remove inventory section
    elif choice == "2":
        inventory_id = input("Enter item name to remove: ").strip().lower()

        if inventory_id in inventories:
            del inventories[inventory_id]
            print(f"{inventory_id} removed successfully.")
        else:
            print("Inventory not found.")
# update inventory section
    elif choice == "3":
        inventory_id = input("Enter item name to update: ").strip().lower()

        if inventory_id in inventories:
            print("1. Update inventory quantity")
            print("2. Update inventory price")

            choice = input("Choose an option: ")
        # update quantity sub-section
            if choice == "1":
                try:
                    new_quantity = int(input("Enter new quantity: "))
                    inventories[inventory_id]["quantity"] = new_quantity
                    print("Quantity updated successfully.")
                except ValueError:
                    print("Please enter a valid whole number.")
        # update price sub-section            
            elif choice == "2":
                try:
                    new_price = float(input("Enter new price: "))
                    inventories[inventory_id]["price"] = new_price
                    print("Price updated successfully.")
                except ValueError:
                    print("Please enter a valid number.")
            else:
                print("Invalid option.")
        else:
            print("Item not found.")
# show all inventory section    
    elif choice == "4":
        if not inventories:
            print("Your inventory is empty. Please add inventory first.")
        else:
            total_inventories_value = 0

            for key, inventory in inventories.items():
                print(f"\nInventory ID: {key}")
                for values in inventory:
                    print(values + ":", inventory[values])

                inventory_item_value = inventory["quantity"] * inventory["price"]
                total_inventories_value += inventory_item_value
            #low stock warning sub-section
                if inventory["quantity"] < 5:
                    print(f"LOW STOCK WARNING: {key} has fewer than 5 items left!")
        # total of inventory section
            print(f"\nTotal Inventory Value: {total_inventories_value:.2f}")
# quit section
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid option. Please choose 1-5.")
