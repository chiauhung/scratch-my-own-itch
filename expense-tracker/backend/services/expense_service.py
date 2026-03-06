"""
Expense Service - Business logic for expense management
"""

import pandas as pd
from typing import Optional, List
from datetime import datetime
from database.sqlite_impl import SQLiteDatabase


class ExpenseService:
    """Service for managing expenses"""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def add_expense(self, date: str, category: str, subcategory: str, amount: float, description: str = "", is_recurring: bool = False):
        """Add a new expense"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        return self.db.add_expense(date, category, subcategory, amount, description, is_recurring)

    def get_expenses(self, start_date: Optional[str] = None, end_date: Optional[str] = None, exclude_recurring: bool = False) -> pd.DataFrame:
        """Get expenses, optionally filtered by date range and excluding recurring"""
        return self.db.get_expenses(start_date, end_date, exclude_recurring)

    def delete_expense(self, expense_id: int):
        """Delete an expense"""
        return self.db.delete_expense(expense_id)

    def update_expense(self, expense_id: int, date: str, category: str, subcategory: str, amount: float, description: str = ""):
        """Update an existing expense"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        success = self.db.update_expense(expense_id, date, category, subcategory, amount, description)
        if not success:
            raise ValueError(f"Expense with id {expense_id} not found")
        return success

    def calculate_summary(self, df: pd.DataFrame) -> dict:
        """Calculate summary statistics from expenses DataFrame"""
        if df.empty:
            return {
                "total": 0.0,
                "average": 0.0,
                "count": 0,
                "highest": 0.0,
                "lowest": 0.0
            }

        return {
            "total": float(df['amount'].sum()),
            "average": float(df['amount'].mean()),
            "count": int(len(df)),
            "highest": float(df['amount'].max()),
            "lowest": float(df['amount'].min())
        }

    def get_spending_by_category(self, df: pd.DataFrame) -> dict:
        """Get total spending grouped by category"""
        if df.empty:
            return {}

        spending = df.groupby('category')['amount'].sum()
        return spending.to_dict()

    def get_spending_by_subcategory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get spending grouped by category and subcategory"""
        if df.empty:
            return pd.DataFrame()

        spending = df.groupby(['category', 'subcategory'])['amount'].sum().reset_index()
        spending.columns = ['category', 'subcategory', 'total']
        return spending.sort_values('total', ascending=False)

    def get_daily_spending(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get daily spending totals"""
        if df.empty:
            return pd.DataFrame(columns=['date', 'amount'])

        daily = df.groupby('date')['amount'].sum().reset_index()
        daily.columns = ['date', 'amount']
        return daily.sort_values('date', ascending=False)

    def get_monthly_spending(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get monthly spending totals"""
        if df.empty:
            return pd.DataFrame(columns=['month', 'amount'])

        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        monthly['month'] = monthly['month'].astype(str)
        monthly.columns = ['month', 'amount']
        return monthly.sort_values('month', ascending=False)

    def get_spending_by_day_of_week(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get average spending by day of week"""
        if df.empty:
            return pd.DataFrame(columns=['day_of_week', 'average_amount'])

        df['day_of_week'] = df['date'].dt.day_name()
        dow = df.groupby('day_of_week')['amount'].mean().reset_index()
        dow.columns = ['day_of_week', 'average_amount']

        # Order by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow['day_of_week'] = pd.Categorical(dow['day_of_week'], categories=day_order, ordered=True)
        dow = dow.sort_values('day_of_week')

        return dow

    def get_top_expenses(self, df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """Get top N expenses by amount"""
        if df.empty:
            return pd.DataFrame()

        return df.nlargest(n, 'amount')

    def search_expenses(self, df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Search expenses by description or subcategory"""
        if df.empty or not search_term:
            return df

        search_term = search_term.lower()
        mask = (
            df['description'].str.lower().str.contains(search_term, na=False) |
            df['subcategory'].str.lower().str.contains(search_term, na=False)
        )
        return df[mask]

    def get_available_months(self) -> List[dict]:
        """
        Get list of available months from earliest expense to current month.
        Returns list of dicts with 'value' (YYYY-MM) and 'display' (e.g., 'October 25')
        """
        # Get all expenses
        df = self.db.get_expenses()

        if df.empty:
            # If no expenses, return just current month
            current = datetime.now()
            month_str = current.strftime("%Y-%m")
            return [{
                "value": month_str,
                "display": self._format_month_display(month_str)
            }]

        # Find earliest expense date
        earliest_date = pd.to_datetime(df['date']).min()
        current_date = datetime.now()

        # Generate all months from earliest to current
        months = []
        current_month = datetime(earliest_date.year, earliest_date.month, 1)
        end_month = datetime(current_date.year, current_date.month, 1)

        while current_month <= end_month:
            month_str = current_month.strftime("%Y-%m")
            months.append({
                "value": month_str,
                "display": self._format_month_display(month_str)
            })
            # Move to next month
            if current_month.month == 12:
                current_month = datetime(current_month.year + 1, 1, 1)
            else:
                current_month = datetime(current_month.year, current_month.month + 1, 1)

        # Return in reverse order (most recent first)
        return list(reversed(months))

    def _format_month_display(self, month_str: str) -> str:
        """
        Format month string from YYYY-MM to display format (e.g., 'October 25')
        """
        date_obj = datetime.strptime(month_str, "%Y-%m")
        month_name = date_obj.strftime("%B")  # Full month name
        year_short = date_obj.strftime("%y")  # 2-digit year
        return f"{month_name} {year_short}"
