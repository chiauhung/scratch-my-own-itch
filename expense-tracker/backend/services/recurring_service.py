"""
Recurring Service - Business logic for recurring transactions
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
from database.sqlite_impl import SQLiteDatabase


class RecurringService:
    """Service for managing recurring transactions"""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def add_recurring_transaction(self, category: str, subcategory: str, amount: float, description: str = ""):
        """Add a new recurring transaction"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        return self.db.add_recurring_transaction(category, subcategory, amount, description)

    def get_recurring_transactions(self) -> pd.DataFrame:
        """Get all recurring transactions"""
        return self.db.get_recurring_transactions()

    def get_active_recurring_transactions(self) -> pd.DataFrame:
        """Get only active recurring transactions"""
        return self.db.get_active_recurring_transactions()

    def update_recurring_amount(self, recurring_id: int, amount: float):
        """Update recurring transaction amount"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        self.db.update_recurring_amount(recurring_id, amount)

    def toggle_recurring_active(self, recurring_id: int, is_active: bool):
        """Toggle recurring transaction active status"""
        self.db.toggle_recurring_active(recurring_id, is_active)

    def delete_recurring_transaction(self, recurring_id: int):
        """Delete a recurring transaction"""
        self.db.delete_recurring_transaction(recurring_id)

    def calculate_total_recurring_amount(self) -> float:
        """Calculate total amount of active recurring transactions"""
        df = self.get_active_recurring_transactions()
        if df.empty:
            return 0.0
        return float(df['amount'].sum())

    def check_month_status(self, month: str) -> Dict:
        """
        Check status of recurring transactions for a month
        Returns: {total_recurring, applied, pending, total_amount, applied_amount, pending_amount}
        """
        active_recurring = self.get_active_recurring_transactions()
        total_recurring = len(active_recurring)
        total_amount = float(active_recurring['amount'].sum()) if not active_recurring.empty else 0.0

        # Check which ones have been applied
        applied_count = 0
        pending_count = 0
        applied_amount = 0.0
        pending_amount = 0.0

        for _, rec in active_recurring.iterrows():
            if self.db.is_recurring_applied(rec['id'], month):
                applied_count += 1
                applied_amount += float(rec['amount'])
            else:
                pending_count += 1
                pending_amount += float(rec['amount'])

        return {
            "total_recurring": total_recurring,
            "applied": applied_count,
            "pending": pending_count,
            "total_amount": total_amount,
            "applied_amount": applied_amount,
            "pending_amount": pending_amount
        }

    def apply_recurring_for_month(self, month: str) -> List[Dict]:
        """
        Apply all pending recurring transactions for a specific month
        Returns list of applied transactions
        """
        active_recurring = self.get_active_recurring_transactions()
        applied = []

        # Parse month to get the first day of the month
        try:
            year, month_num = month.split('-')
            date = f"{year}-{month_num}-01"
        except:
            raise ValueError(f"Invalid month format: {month}. Expected YYYY-MM")

        for _, rec in active_recurring.iterrows():
            # Check if already applied
            if not self.db.is_recurring_applied(rec['id'], month):
                # Add as expense with recurring flag
                expense_id = self.db.add_expense(
                    date=date,
                    category=rec['category'],
                    subcategory=rec['subcategory'],
                    amount=rec['amount'],
                    description=f"[Recurring] {rec['description']}",
                    is_recurring=True
                )

                # Mark as applied
                self.db.mark_recurring_applied(rec['id'], month, expense_id)

                applied.append({
                    "recurring_id": int(rec['id']),
                    "expense_id": expense_id,
                    "category": rec['category'],
                    "subcategory": rec['subcategory'],
                    "amount": float(rec['amount']),
                    "description": rec['description']
                })

        return applied

    def setup_default_recurring(self):
        """Setup default recurring transactions if none exist"""
        existing = self.get_recurring_transactions()

        if existing.empty:
            # Add some default recurring transactions
            default_recurring = [
                {
                    "category": "固定支出 (Fixed)",
                    "subcategory": "房租 (Rent)",
                    "amount": 1500.00,
                    "description": "Monthly rent payment"
                },
                {
                    "category": "固定支出 (Fixed)",
                    "subcategory": "房屋水电 (Utilities)",
                    "amount": 150.00,
                    "description": "Electricity and water"
                },
                {
                    "category": "固定支出 (Fixed)",
                    "subcategory": "网络电话 (Internet/Phone)",
                    "amount": 100.00,
                    "description": "Internet and phone bills"
                }
            ]

            for rec in default_recurring:
                self.add_recurring_transaction(**rec)

    def get_recurring_by_category(self) -> Dict[str, List[Dict]]:
        """Get recurring transactions grouped by category"""
        df = self.get_recurring_transactions()

        if df.empty:
            return {}

        grouped = {}
        for category in df['category'].unique():
            category_data = df[df['category'] == category]
            grouped[category] = category_data.to_dict('records')

        return grouped
