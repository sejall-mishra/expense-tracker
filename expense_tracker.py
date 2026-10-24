import os
import sqlite3
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "expenses.db")
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Other"]


class ExpenseDB:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.create_table()

    def create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, amount, category, description, expense_date):
        self.conn.execute(
            "INSERT INTO expenses (amount, category, description, date) "
            "VALUES (?, ?, ?, ?)",
            (amount, category, description, expense_date),
        )
        self.conn.commit()

    def all(self):
        cursor = self.conn.execute(
            "SELECT id, date, category, amount, description "
            "FROM expenses ORDER BY date DESC, id DESC"
        )
        return cursor.fetchall()

    def delete(self, expense_id):
        cursor = self.conn.execute(
            "DELETE FROM expenses WHERE id = ?", (expense_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def total(self):
        cursor = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        )
        return cursor.fetchone()[0]

    def by_category(self):
        cursor = self.conn.execute(
            "SELECT category, SUM(amount) FROM expenses "
            "GROUP BY category ORDER BY SUM(amount) DESC"
        )
        return cursor.fetchall()

    def close(self):
        self.conn.close()


def get_amount():
    while True:
        value = input("Amount (Rs.): ").strip()
        try:
            amount = float(value)
        except ValueError:
            print("Please type a number.")
            continue
        if amount <= 0:
            print("Amount must be more than 0.")
            continue
        return amount


def get_category():
    print("Categories:")
    for i, name in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {name}")
    while True:
        choice = input(f"Choose a category (1-{len(CATEGORIES)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        print("Please choose a valid number.")


def get_date():
    while True:
        value = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
        if value == "":
            return date.today().isoformat()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Please use the format YYYY-MM-DD, for example 2026-10-24.")


def add_expense(db):
    amount = get_amount()
    category = get_category()
    description = input("Description (optional): ").strip()
    expense_date = get_date()
    db.add(amount, category, description, expense_date)
    print("Expense added!")


def show_expenses(db):
    rows = db.all()
    if not rows:
        print("\nNo expenses yet.")
        return
    print(f"\n{'ID':<4} {'Date':<11} {'Category':<10} {'Amount':>10}  Description")
    print("-" * 55)
    for expense_id, expense_date, category, amount, description in rows:
        print(
            f"{expense_id:<4} {expense_date:<11} {category:<10} "
            f"{amount:>10.2f}  {description}"
        )


def delete_expense(db):
    show_expenses(db)
    value = input("\nEnter the ID to delete (or press Enter to cancel): ").strip()
    if not value:
        return
    if not value.isdigit():
        print("Please type a valid ID number.")
        return
    if db.delete(int(value)):
        print("Expense deleted.")
    else:
        print("No expense found with that ID.")


def show_summary(db):
    rows = db.by_category()
    if not rows:
        print("\nNo expenses yet.")
        return
    print("\n=== Spending by category ===")
    for category, amount in rows:
        print(f"{category:<10} Rs. {amount:.2f}")
    print("-" * 24)
    print(f"{'Total':<10} Rs. {db.total():.2f}")


def main():
    db = ExpenseDB(DB_FILE)
    print("Welcome to the Expense Tracker!")

    while True:
        print("\n1. Add expense")
        print("2. View all expenses")
        print("3. Delete an expense")
        print("4. Summary by category")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense(db)
        elif choice == "2":
            show_expenses(db)
        elif choice == "3":
            delete_expense(db)
        elif choice == "4":
            show_summary(db)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 5.")

    db.close()


if __name__ == "__main__":
    main()