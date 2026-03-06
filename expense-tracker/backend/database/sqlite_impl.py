"""
SQLite Database Implementation for Expense Tracker
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional


class SQLiteDatabase:
    """SQLite database for expense tracking"""

    def __init__(self, db_path: str):
        """Initialize database with path"""
        self.db_path = db_path

        # Create directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize tables
        self._init_tables()

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if we need to migrate existing expenses table
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [row[1] for row in cursor.fetchall()]

        if columns and 'is_recurring' not in columns:
            # Migration: Add is_recurring column to existing table
            cursor.execute("ALTER TABLE expenses ADD COLUMN is_recurring INTEGER DEFAULT 0")
            conn.commit()

        # Expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                is_recurring INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(month, category)
            )
        """)

        # Recurring transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Applied recurring table (tracks which recurring transactions have been applied for each month)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applied_recurring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recurring_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                expense_id INTEGER NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recurring_id) REFERENCES recurring_transactions(id),
                FOREIGN KEY (expense_id) REFERENCES expenses(id),
                UNIQUE(recurring_id, month)
            )
        """)

        conn.commit()
        conn.close()

    # ============= Expenses =============

    def add_expense(self, date: str, category: str, subcategory: str, amount: float, description: str = "", is_recurring: bool = False):
        """Add a new expense"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses (date, category, subcategory, amount, description, is_recurring)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, category, subcategory, amount, description, 1 if is_recurring else 0))

        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return expense_id

    def get_expenses(self, start_date: Optional[str] = None, end_date: Optional[str] = None, exclude_recurring: bool = False) -> pd.DataFrame:
        """Get expenses, optionally filtered by date range and excluding recurring"""
        conn = self._get_connection()

        # Build WHERE clause
        where_clauses = []
        params = []

        if start_date and end_date:
            where_clauses.append("date BETWEEN ? AND ?")
            params.extend([start_date, end_date])
        elif start_date:
            where_clauses.append("date >= ?")
            params.append(start_date)
        elif end_date:
            where_clauses.append("date <= ?")
            params.append(end_date)

        if exclude_recurring:
            where_clauses.append("is_recurring = 0")

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"SELECT * FROM expenses WHERE {where_clause} ORDER BY date DESC"

        if params:
            df = pd.read_sql_query(query, conn, params=tuple(params))
        else:
            df = pd.read_sql_query(query, conn)

        conn.close()

        # Convert date column to datetime
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])

        return df

    def delete_expense(self, expense_id: int):
        """Delete an expense by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

        conn.commit()
        conn.close()

    def update_expense(self, expense_id: int, date: str, category: str, subcategory: str, amount: float, description: str = ""):
        """Update an existing expense"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE expenses
            SET date = ?, category = ?, subcategory = ?, amount = ?, description = ?
            WHERE id = ?
        """, (date, category, subcategory, amount, description, expense_id))

        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        return rows_affected > 0

    def get_expense_by_id(self, expense_id: int) -> Optional[dict]:
        """Get a specific expense by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    # ============= Budgets =============

    def set_budget(self, month: str, category: str, amount: float):
        """Set budget for a category in a specific month"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO budgets (month, category, amount)
            VALUES (?, ?, ?)
        """, (month, category, amount))

        conn.commit()
        conn.close()

    def get_budget(self, month: str, category: str) -> Optional[float]:
        """Get budget for a category in a specific month"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT amount FROM budgets
            WHERE month = ? AND category = ?
        """, (month, category))

        row = cursor.fetchone()
        conn.close()

        if row:
            return row['amount']
        return None

    def get_all_budgets(self, month: str) -> dict:
        """Get all budgets for a specific month"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, amount FROM budgets
            WHERE month = ?
        """, (month,))

        rows = cursor.fetchall()
        conn.close()

        return {row['category']: row['amount'] for row in rows}

    # ============= Recurring Transactions =============

    def add_recurring_transaction(self, category: str, subcategory: str, amount: float, description: str = ""):
        """Add a new recurring transaction"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO recurring_transactions (category, subcategory, amount, description)
            VALUES (?, ?, ?, ?)
        """, (category, subcategory, amount, description))

        recurring_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return recurring_id

    def get_recurring_transactions(self) -> pd.DataFrame:
        """Get all recurring transactions"""
        conn = self._get_connection()
        query = "SELECT * FROM recurring_transactions ORDER BY category, subcategory"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_active_recurring_transactions(self) -> pd.DataFrame:
        """Get only active recurring transactions"""
        conn = self._get_connection()
        query = """
            SELECT * FROM recurring_transactions
            WHERE is_active = 1
            ORDER BY category, subcategory
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def update_recurring_amount(self, recurring_id: int, amount: float):
        """Update recurring transaction amount"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE recurring_transactions
            SET amount = ?
            WHERE id = ?
        """, (amount, recurring_id))

        conn.commit()
        conn.close()

    def toggle_recurring_active(self, recurring_id: int, is_active: bool):
        """Toggle recurring transaction active status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE recurring_transactions
            SET is_active = ?
            WHERE id = ?
        """, (1 if is_active else 0, recurring_id))

        conn.commit()
        conn.close()

    def delete_recurring_transaction(self, recurring_id: int):
        """Delete a recurring transaction"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Also delete any applied records
        cursor.execute("DELETE FROM applied_recurring WHERE recurring_id = ?", (recurring_id,))
        cursor.execute("DELETE FROM recurring_transactions WHERE id = ?", (recurring_id,))

        conn.commit()
        conn.close()

    def get_applied_recurring(self, month: str) -> pd.DataFrame:
        """Get applied recurring transactions for a month"""
        conn = self._get_connection()
        query = """
            SELECT ar.*, rt.category, rt.subcategory, rt.amount, rt.description
            FROM applied_recurring ar
            JOIN recurring_transactions rt ON ar.recurring_id = rt.id
            WHERE ar.month = ?
        """
        df = pd.read_sql_query(query, conn, params=(month,))
        conn.close()
        return df

    def mark_recurring_applied(self, recurring_id: int, month: str, expense_id: int):
        """Mark a recurring transaction as applied for a specific month"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO applied_recurring (recurring_id, month, expense_id)
            VALUES (?, ?, ?)
        """, (recurring_id, month, expense_id))

        conn.commit()
        conn.close()

    def is_recurring_applied(self, recurring_id: int, month: str) -> bool:
        """Check if a recurring transaction has been applied for a specific month"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM applied_recurring
            WHERE recurring_id = ? AND month = ?
        """, (recurring_id, month))

        row = cursor.fetchone()
        conn.close()

        return row['count'] > 0
