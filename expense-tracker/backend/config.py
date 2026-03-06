"""
Configuration file for Expense Tracker
Defines categories, subcategories, and default budgets
"""

# Expense Categories with Subcategories
CATEGORIES = {
    "固定支出 (Fixed Expenses)": ["房屋水电", "WiFi/保险/Digi/Yes", "家人"],
    "生活必要支出 (Essential Living)": ["Food", "Transport", "Lens"],
    "生活质量支出 (Quality of Life)": ["Music", "Sports", "Game", "Others", "Work"],
    "基金 (Fund/Savings)": ["Health/Travel/Wishlist", "Maintenance", "Savings"],
}

# Default monthly budgets (in RM - Malaysian Ringgit)
DEFAULT_BUDGETS = {
    "固定支出 (Fixed Expenses)": 3000.00,
    "生活必要支出 (Essential Living)": 1500.00,
    "生活质量支出 (Quality of Life)": 1000.00,
    "基金 (Fund/Savings)": 2000.00,
}

# Currency
CURRENCY = "RM"
CURRENCY_SYMBOL = "RM"
