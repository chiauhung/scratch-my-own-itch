"""
Migration script to remove numbering from category names
Run this once to update existing database records
"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "expenses.db")

# Category name mapping (old -> new)
CATEGORY_MAPPING = {
    "1. 固定支出 (Fixed Expenses)": "固定支出 (Fixed Expenses)",
    "2. 生活必要支出 (Essential Living)": "生活必要支出 (Essential Living)",
    "3. 生活质量支出 (Quality of Life)": "生活质量支出 (Quality of Life)",
    "4. 基金 (Fund/Savings)": "基金 (Fund/Savings)",
}

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Starting migration to remove category numbering...")

    # Update expenses table
    for old_name, new_name in CATEGORY_MAPPING.items():
        cursor.execute("""
            UPDATE expenses
            SET category = ?
            WHERE category = ?
        """, (new_name, old_name))
        print(f"  Updated {cursor.rowcount} expenses from '{old_name}' to '{new_name}'")

    # Update budgets table
    for old_name, new_name in CATEGORY_MAPPING.items():
        cursor.execute("""
            UPDATE budgets
            SET category = ?
            WHERE category = ?
        """, (new_name, old_name))
        print(f"  Updated {cursor.rowcount} budgets from '{old_name}' to '{new_name}'")

    # Update recurring_transactions table
    for old_name, new_name in CATEGORY_MAPPING.items():
        cursor.execute("""
            UPDATE recurring_transactions
            SET category = ?
            WHERE category = ?
        """, (new_name, old_name))
        print(f"  Updated {cursor.rowcount} recurring transactions from '{old_name}' to '{new_name}'")

    conn.commit()
    conn.close()

    print("\nMigration completed successfully!")
    print("All category names have been updated to remove numbering.")

if __name__ == "__main__":
    migrate()
