from db import Database
from manager import RestaurantManager
from colorama import init, Fore, Style

init(autoreset=True)


def main_menu():
    print("\n=========================================")
    print("     🍽️  Restaurant Management System   ")
    print("=========================================")
    print("1. Show Menu")
    print("2. Show Table Status")
    print("3. Add New Order")
    print("4. Update Order Status")
    print("5. View Order Details & Total Price")
    print("6. Show Daily Sales Report")
    print("7. Manage Tables")
    print("8. Manage Menu")
    print("9. Exit")
    print("-----------------------------------------")


def manage_tables_menu(manager: RestaurantManager):
    while True:
        print("\n--- Table Management ---")
        print("1. Add a new table")
        print("2. Remove a table")
        print("3. Back to main menu")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            tn = input("Enter table number: ").strip()
            if not tn.isdigit():
                print("Invalid number.")
                continue
            manager.add_table(int(tn))
        elif choice == "2":
            tn = input("Enter table number to remove: ").strip()
            if not tn.isdigit():
                print("Invalid number.")
                continue
            manager.remove_table(int(tn))
        elif choice == "3":
            break
        else:
            print("Invalid choice!")


def manage_menu_menu(manager: RestaurantManager):
    while True:
        print("\n--- Menu Management ---")
        print("1. Add a new menu item")
        print("2. Edit item price")
        print("3. Delete a item")
        print("4. Show menu")
        print("5. Back to main menu")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            name = input("Enter item name: ").strip()
            price_raw = input("Enter item price: ").strip()
            try:
                price = float(price_raw)
                if price < 0:
                    raise ValueError
            except Exception:
                print("Invalid price.")
                continue
            manager.add_menu_item(name, price)
        elif choice == "2":
            item_id_raw = input("Enter item ID to edit: ").strip()
            if not item_id_raw.isdigit():
                print("Invalid ID.")
                continue
            new_price_raw = input("Enter new price: ").strip()
            try:
                new_price = float(new_price_raw)
                if new_price < 0:
                    raise ValueError
            except Exception:
                print("Invalid price.")
                continue
            manager.edit_menu_item_price(int(item_id_raw), new_price)
        elif choice == "3":
            item_id_raw = input("Enter item ID to delete: ").strip()
            if not item_id_raw.isdigit():
                print("Invalid ID.")
                continue
            manager.delete_menu_item(int(item_id_raw))
        elif choice == "4":
            manager.show_menu()
        elif choice == "5":
            break
        else:
            print("Invalid choice!")


def run():
    db = Database()
    mgr = RestaurantManager(db)
    while True:
        main_menu()
        choice = input("Please select an option (1-9): ").strip()
        if choice == "1":
            mgr.show_menu()
        elif choice == "2":
            mgr.show_tables_status()
        elif choice == "3":
            tn = input("Enter table number for the new order: ").strip()
            if not tn.isdigit():
                print("Invalid table number.")
                continue
            table_number = int(tn)
            # show menu to user
            mgr.show_menu()
            items = []
            while True:
                item_id_raw = input("Enter item ID to add (or 0 to finish): ").strip()
                if not item_id_raw.isdigit():
                    print("Invalid id.")
                    continue
                item_id = int(item_id_raw)
                if item_id == 0:
                    break
                qty_raw = input(f"Enter quantity for item id {item_id}: ").strip()
                if not qty_raw.isdigit() or int(qty_raw) <= 0:
                    print("Invalid quantity.")
                    continue
                items.append((item_id, int(qty_raw)))
                print(Fore.GREEN + f"✔️ Added item id {item_id} (x{qty_raw})" + Style.RESET_ALL)
            if not items:
                print("No items added. Cancelled order.")
                continue
            try:
                mgr.add_order(table_number, items)
            except Exception as e:
                print(Fore.RED + f"Error creating order: {e}" + Style.RESET_ALL)
        elif choice == "4":
            oid = input("Enter Order ID: ").strip()
            if not oid.isdigit():
                print("Invalid Order ID.")
                continue
            order = db.fetchone("SELECT id, status FROM orders WHERE id=%s", (int(oid),))
            if not order:
                print("Order not found.")
                continue
            print(f"Current status: {order['status']}")
            print("Select new status:")
            print("1. received")
            print("2. preparing")
            print("3. ready")
            print("4. paid")
            s = input("Your choice: ").strip()
            map_status = {"1": "received", "2": "preparing", "3": "ready", "4": "paid"}
            if s not in map_status:
                print("Invalid choice.")
                continue
            mgr.update_order_status(int(oid), map_status[s])
        elif choice == "5":
            oid = input("Enter Order ID: ").strip()
            if not oid.isdigit():
                print("Invalid Order ID.")
                continue
            mgr.show_order_details(int(oid))
        elif choice == "6":
            mgr.get_daily_sales_report()
        elif choice == "7":
            manage_tables_menu(mgr)
        elif choice == "8":
            manage_menu_menu(mgr)
        elif choice == "9":
            print(Fore.CYAN + "Goodbye!" + Style.RESET_ALL)
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    run()
