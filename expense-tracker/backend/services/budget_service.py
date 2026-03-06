"""
Budget Service - Business logic for budget management
"""

from typing import Dict, Optional
from database.sqlite_impl import SQLiteDatabase
from config import DEFAULT_BUDGETS


class BudgetService:
    """Service for managing budgets"""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def set_budget(self, month: str, category: str, amount: float):
        """Set budget for a category"""
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")

        self.db.set_budget(month, category, amount)

    def get_budget(self, month: str, category: str) -> float:
        """Get budget for a category, returns default if not set"""
        budget = self.db.get_budget(month, category)

        if budget is None:
            # Return default budget if not set
            return DEFAULT_BUDGETS.get(category, 0.0)

        return budget

    def get_all_budgets(self, month: str) -> Dict[str, float]:
        """Get all budgets for a month, fills in defaults for missing categories"""
        budgets = self.db.get_all_budgets(month)

        # Fill in defaults for categories not yet set
        result = DEFAULT_BUDGETS.copy()
        result.update(budgets)

        return result

    def set_multiple_budgets(self, month: str, budgets: Dict[str, float]):
        """Set multiple budgets at once"""
        for category, amount in budgets.items():
            if amount < 0:
                raise ValueError(f"Budget amount for {category} cannot be negative")
            self.db.set_budget(month, category, amount)

    def calculate_budget_comparison(self, month: str, spending: Dict[str, float]) -> Dict[str, dict]:
        """
        Compare budgets vs actual spending
        Returns dict with budget, spent, remaining, and percentage for each category
        """
        budgets = self.get_all_budgets(month)
        comparison = {}

        for category, budget in budgets.items():
            spent = spending.get(category, 0.0)
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0

            comparison[category] = {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage
            }

        return comparison

    def calculate_total_budget_summary(self, comparison: Dict[str, dict]) -> dict:
        """Calculate total budget summary from comparison"""
        total_budget = sum(cat["budget"] for cat in comparison.values())
        total_spent = sum(cat["spent"] for cat in comparison.values())
        total_remaining = total_budget - total_spent
        total_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0

        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "total_percentage": total_percentage
        }

    def get_overspent_categories(self, month: str, spending: Dict[str, float]) -> Dict[str, dict]:
        """Get categories that are over budget"""
        comparison = self.calculate_budget_comparison(month, spending)
        return {
            cat: data for cat, data in comparison.items()
            if data["percentage"] > 100
        }

    def get_budget_warnings(self, month: str, spending: Dict[str, float], threshold: float = 80.0) -> Dict[str, dict]:
        """Get categories approaching budget limit"""
        comparison = self.calculate_budget_comparison(month, spending)
        return {
            cat: data for cat, data in comparison.items()
            if threshold <= data["percentage"] <= 100
        }
