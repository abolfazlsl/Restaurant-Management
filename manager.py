from db import Database
from models import MenuItem, Table, Order, OrderItem
from typing import List, Optional
from colorama import init, Fore, Style
from datetime import date

init(autoreset=True)

class RestaurantManager:
    def __init__(self, db: Database):
        self.db = db

    # ---------- Menu (menu_items) ----------
    def add_menu_item(self, name: str, price: float) -> None:
        # ensure unique name
        existing = self.db.fetchone("SELECT id FROM menu_items WHERE LOWER(name)=LOWER(%s)", (name,))
        if existing:
            print(Fore.RED + "❌ Menu item already exists." + Style.RESET_ALL)
            return
        self.db.execute("INSERT INTO menu_items (name, price) VALUES (%s, %s)", (name, price))
        print(Fore.GREEN + f"✅ Added menu item: {name}" + Style.RESET_ALL)

    def edit_menu_item_price(self, item_id: int, new_price: float) -> None:
        exists = self.db.fetchone("SELECT id FROM menu_items WHERE id=%s", (item_id,))
        if not exists:
            print(Fore.RED + "❌ Menu item not found." + Style.RESET_ALL)
            return
        self.db.execute("UPDATE menu_items SET price=%s WHERE id=%s", (new_price, item_id))
        print(Fore.GREEN + "✅ Price updated." + Style.RESET_ALL)

    def show_menu(self) -> None:
        rows = self.db.fetchall("SELECT id, name, price FROM menu_items ORDER BY id")
        if not rows:
            print(f"{Fore.YELLOW}⚠️  No menu items found. Please add items first.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}========= 📋 MENU ========={Style.RESET_ALL}")
        print(f"{'ID':<4} {'Name':<20} {'Price'}")
        print("-" * 40)
        for r in rows:
            print(f"{r['id']:<4} {r['name']:<20} {int(r['price']):>8}")
        print("=" * 40)

    def delete_menu_item(self , item_id: int) -> None:
        exists = self.db.fetchone("SELECT id FROM menu_items WHERE id=%s", (item_id,))
        if not exists:
            print(Fore.RED + "❌ Menu item not found." + Style.RESET_ALL)
            return
        used = self.db.fetchone("SELECT COUNT(*) AS cnt FROM order_details WHERE item_id=%s", (item_id,))
        if used and used.get('cnt', 0) > 0:
            print(Fore.RED + "❌ Cannot delete: item is used in orders." + Style.RESET_ALL)
            return
        self.db.execute("DELETE FROM menu_items WHERE id=%s", (item_id,))
        print(f"{Fore.GREEN}✅ Item deleted.{Style.RESET_ALL}")

    # ---------- Tables ----------
    def add_table(self, table_number: int) -> None:
        exists = self.db.fetchone("SELECT id FROM tables WHERE table_number=%s", (table_number,))
        if exists:
            print(Fore.RED + "❌ Table number already exists." + Style.RESET_ALL)
            return
        self.db.execute("INSERT INTO tables (table_number, status) VALUES (%s, 'available')", (table_number,))
        print(Fore.GREEN + f"✅ Added table #{table_number}" + Style.RESET_ALL)

    def remove_table(self, table_number: int) -> None:
        tbl = self.db.fetchone("SELECT id, status FROM tables WHERE table_number=%s", (table_number,))
        if not tbl:
            print(Fore.RED + "❌ Table not found." + Style.RESET_ALL)
            return
        if tbl['status'] == 'occupied':
            print(Fore.RED + "❌ Cannot remove an occupied table." + Style.RESET_ALL)
            return
        self.db.execute("DELETE FROM tables WHERE table_number=%s", (table_number,))
        print(Fore.YELLOW + f"🗑️ Removed table #{table_number}" + Style.RESET_ALL)

    def show_tables_status(self) -> None:
        rows = self.db.fetchall("SELECT table_number, status FROM tables ORDER BY table_number")
        if not rows:
            print(f"{Fore.YELLOW}⚠️  No tables found. Please add tables first.{Style.RESET_ALL}")
            return
        print(f"\n{Fore.CYAN}========= 🪑 Tables ========={Style.RESET_ALL}")
        print(f"{'Table':<8}{'Status'}")
        print("-" * 25)
        for r in rows:
            print(f"{r['table_number']:<8}{r['status']}")
        print("=" * 25)

    def update_table_status(self, table_number: int, status: str) -> None:
        if status not in ('available','occupied'):
            print(Fore.RED + "❌ Invalid status." + Style.RESET_ALL)
            return
        self.db.execute("UPDATE tables SET status=%s WHERE table_number=%s", (status, table_number))
        print(Fore.GREEN + f"✅ Table #{table_number} set to {status}" + Style.RESET_ALL)

    # ---------- Orders ----------
    def add_order(self, table_number: int, items: List[tuple]) -> None:
        """
        items: list of tuples (item_id, quantity)
        """
        tbl = self.db.fetchone("SELECT id, status FROM tables WHERE table_number=%s", (table_number,))
        if not tbl:
            print(Fore.RED + "❌ Table not found." + Style.RESET_ALL)
            return
        if tbl['status'] == 'occupied':
            print(Fore.YELLOW + f"⚠️ Error: Table #{table_number} is currently occupied. Please choose another table." + Style.RESET_ALL)
            return

        # create order
        with self.db.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO orders (table_id, status) VALUES (%s, %s) RETURNING id", (tbl['id'], 'received'))
                order_id = cur.fetchone()[0]
                # insert order_details
                for item_id, qty in items:
                    # validate menu item exists
                    cur.execute("SELECT id, name FROM menu_items WHERE id=%s", (item_id,))
                    mi = cur.fetchone()
                    if not mi:
                        raise ValueError(f"Menu item id {item_id} not found")
                    cur.execute("INSERT INTO order_details (order_id, item_id, quantity) VALUES (%s,%s,%s)", (order_id, item_id, qty))
                # mark table occupied
                cur.execute("UPDATE tables SET status='occupied' WHERE id=%s", (tbl['id'],))
        print(Fore.GREEN + f"🎉 Order #{order_id} created successfully for Table #{table_number}!" + Style.RESET_ALL)

    def update_order_status(self, order_id: int, new_status: str) -> None:
        if new_status not in ('received','preparing','ready','paid'):
            print(Fore.RED + "❌ Invalid status choice." + Style.RESET_ALL)
            return
        order = self.db.fetchone("SELECT id, table_id, status FROM orders WHERE id=%s", (order_id,))
        if not order:
            print(Fore.RED + "❌ Order not found." + Style.RESET_ALL)
            return
        self.db.execute("UPDATE orders SET status=%s WHERE id=%s", (new_status, order_id))
        print(Fore.GREEN + f"✅ Order #{order_id} marked as {new_status.upper()}." + Style.RESET_ALL)
        if new_status == 'paid':
            # free table
            self.db.execute("UPDATE tables SET status='available' WHERE id=%s", (order['table_id'],))
            print(Fore.CYAN + f"🪑 Table is now AVAILABLE again." + Style.RESET_ALL)

    def show_active_orders(self) -> None:
        rows = self.db.fetchall("""
            SELECT o.id, t.table_number, o.status, o.order_time
            FROM orders o JOIN tables t ON o.table_id = t.id
            WHERE o.status != 'paid'
            ORDER BY o.order_time
        """)
        print(f"\n{Fore.CYAN}--- Active Orders ---{Style.RESET_ALL}")
        if not rows:
            print("No active orders.")
            return
        for r in rows:
            print(f"Order #{r['id']} | Table #{r['table_number']} | Status: {r['status']} | Time: {r['order_time']}")

    def show_order_details(self, order_id: int) -> None:
        # order summary
        order = self.db.fetchone("""
            SELECT o.id, o.status, o.order_time, t.table_number
            FROM orders o JOIN tables t ON o.table_id = t.id
            WHERE o.id = %s
        """, (order_id,))
        if not order:
            print(Fore.RED + "❌ Order not found." + Style.RESET_ALL)
            return
        details = self.db.fetchall("""
            SELECT m.name, m.price, od.quantity, (m.price * od.quantity) as total
            FROM order_details od
            JOIN menu_items m ON od.item_id = m.id
            WHERE od.order_id = %s
        """, (order_id,))
        print(f"\n{Fore.CYAN}========= 🧾 Order #{order_id} ========={Style.RESET_ALL}")
        print(f"{'Item':<15}{'Qty':>6}{'Price':>10}{'Total':>12}")
        print("-" * 45)
        total = 0
        for d in details:
            print(f"{d['name']:<15}{d['quantity']:>6}{int(d['price']):>10}{int(d['total']):>12}")
            total += float(d['total'])
        print("-" * 45)
        print(f"{'Total:':<15}{'':>6}{'':>10}{int(total):>12}")
        print(f"Status: {order['status']}")
        print(f"Table: #{order['table_number']}")
        print("=" * 45)

    def get_daily_sales_report(self, for_date: Optional[date] = None) -> None:
        if for_date is None:
            for_date = date.today()
        # sum totals for orders marked 'paid' on that day
        rows = self.db.fetchall("""
            SELECT o.id, o.order_time
            FROM orders o
            WHERE o.status = 'paid' AND DATE(o.order_time) = %s
        """, (for_date,))
        total_orders = len(rows)
        # compute revenue
        rev = self.db.fetchone("""
            SELECT SUM(m.price * od.quantity) as total_sales
            FROM orders o
            JOIN order_details od ON od.order_id = o.id
            JOIN menu_items m ON m.id = od.item_id
            WHERE o.status = 'paid' AND DATE(o.order_time) = %s
        """, (for_date,))
        total_sales = int(rev['total_sales']) if rev and rev['total_sales'] else 0
        paid_count = total_orders
        unpaid_rows = self.db.fetchall("""
            SELECT id FROM orders WHERE status != 'paid' AND DATE(order_time) = %s
        """, (for_date,))
        unpaid_count = len(unpaid_rows)
        print(f"\n{Fore.CYAN}========= 📊 Daily Sales ========={Style.RESET_ALL}")
        print(f"Date: {for_date.isoformat()}")
        print()
        print(f"Total Orders: {total_orders}")
        print(f"Paid Orders: {paid_count}")
        print(f"Unpaid Orders: {unpaid_count}")
        print()
        print(f"Total Sales: {total_sales:,}")
        print("=" * 40)
