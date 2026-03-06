"""
FastAPI Backend for Life Dashboard.
Integrated platform for managing expenses, habits, savings, and journaling.

Clean architecture with services and database layers.

Modules:
  - Expense Tracker (ACTIVE)
  - Habit Tracker (PLANNED)
  - Savings & Investment (PLANNED)
  - Journal (PLANNED)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import os

# Import configuration
from config import CATEGORIES, DEFAULT_BUDGETS
from database.sqlite_impl import SQLiteDatabase

# Import active services
from services.expense_service import ExpenseService
from services.budget_service import BudgetService
from services.recurring_service import RecurringService

# Import meal planner service
from services.meal_service import MealService

# Import placeholder services (to be implemented)
# from services.savings_service import SavingsService
# from services.journal_service import JournalService

# Initialize FastAPI app
app = FastAPI(
    title="Life Dashboard API",
    version="2.0.0",
    description="Unified API for expense tracking, habits, savings, and journaling"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with local database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "expenses.db")
db = SQLiteDatabase(DATABASE_PATH)
expense_service = ExpenseService(db)
budget_service = BudgetService(db)
recurring_service = RecurringService(db)
meal_service = MealService(db)

# Setup default recurring transactions
recurring_service.setup_default_recurring()

# Pydantic models for request/response
class ExpenseCreate(BaseModel):
    date: str
    category: str
    subcategory: str
    amount: float
    description: str = ""

class BudgetUpdate(BaseModel):
    budgets: dict[str, float]

class RecurringCreate(BaseModel):
    category: str
    subcategory: str
    amount: float
    description: str = "Recurring monthly expense"

class RecurringUpdate(BaseModel):
    amount: Optional[float] = None
    is_active: Optional[bool] = None

class RecipeCreate(BaseModel):
    name: str
    category: str
    ingredients: str
    instructions: str = ""
    servings: int = 4
    prep_time: int = 30
    nutrition_info: Optional[str] = None

class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    nutrition_info: Optional[str] = None

class MealPlanCreate(BaseModel):
    date: str
    meal_type: str
    recipe_id: int
    notes: str = ""

class MealPlanUpdate(BaseModel):
    date: Optional[str] = None
    meal_type: Optional[str] = None
    recipe_id: Optional[int] = None
    notes: Optional[str] = None

# ============= API Endpoints =============

@app.get("/")
def root():
    return {"message": "Ocean Expense Tracker API", "version": "1.0.0"}

@app.get("/config/categories")
def get_categories():
    """Get expense categories"""
    return {"categories": CATEGORIES}

@app.get("/config/default-budgets")
def get_default_budgets():
    """Get default budget amounts"""
    return {"budgets": DEFAULT_BUDGETS}

# ============= Expenses =============

@app.get("/expenses")
def get_expenses(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get all expenses, optionally filtered by date range"""
    df = expense_service.get_expenses(start_date, end_date)
    return {"expenses": df.to_dict(orient="records")}

@app.post("/expenses")
def add_expense(expense: ExpenseCreate):
    """Add a new expense"""
    try:
        expense_service.add_expense(
            expense.date,
            expense.category,
            expense.subcategory,
            expense.amount,
            expense.description
        )
        return {"message": "Expense added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    """Delete an expense"""
    try:
        expense_service.delete_expense(expense_id)
        return {"message": "Expense deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseCreate):
    """Update an existing expense"""
    try:
        expense_service.update_expense(
            expense_id,
            expense.date,
            expense.category,
            expense.subcategory,
            expense.amount,
            expense.description
        )
        return {"message": "Expense updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/expenses/summary")
def get_summary(start_date: Optional[str] = None, end_date: Optional[str] = None, exclude_recurring: bool = True):
    """Get expense summary statistics (excludes recurring by default)"""
    df = expense_service.get_expenses(start_date, end_date, exclude_recurring)
    summary = expense_service.calculate_summary(df)
    return {"summary": summary}

@app.get("/expenses/by-category")
def get_spending_by_category(start_date: Optional[str] = None, end_date: Optional[str] = None, exclude_recurring: bool = True):
    """Get spending grouped by category (excludes recurring by default)"""
    df = expense_service.get_expenses(start_date, end_date, exclude_recurring)
    spending = expense_service.get_spending_by_category(df)
    return {"spending": spending}

@app.get("/expenses/by-subcategory")
def get_spending_by_subcategory(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get spending grouped by subcategory"""
    df = expense_service.get_expenses(start_date, end_date)
    spending_df = expense_service.get_spending_by_subcategory(df)
    return {"spending": spending_df.to_dict(orient="records")}

@app.get("/expenses/daily")
def get_daily_spending(start_date: Optional[str] = None, end_date: Optional[str] = None, exclude_recurring: bool = True):
    """Get daily spending totals (excludes recurring by default for trends)"""
    df = expense_service.get_expenses(start_date, end_date, exclude_recurring)
    daily_df = expense_service.get_daily_spending(df)
    # Convert date to string for JSON serialization
    if not daily_df.empty and 'date' in daily_df.columns:
        daily_df['date'] = daily_df['date'].dt.strftime('%Y-%m-%d')
    return {"daily": daily_df.to_dict(orient="records")}

@app.get("/expenses/monthly")
def get_monthly_spending():
    """Get monthly spending totals"""
    df = expense_service.get_expenses()
    monthly_df = expense_service.get_monthly_spending(df)
    return {"monthly": monthly_df.to_dict(orient="records")}

@app.get("/expenses/by-day-of-week")
def get_spending_by_day_of_week():
    """Get average spending by day of week"""
    df = expense_service.get_expenses()
    dow_df = expense_service.get_spending_by_day_of_week(df)
    return {"day_of_week": dow_df.to_dict(orient="records")}

@app.get("/expenses/available-months")
def get_available_months():
    """Get list of available months from earliest expense to current month"""
    months = expense_service.get_available_months()
    return {"months": months}

# ============= Budgets =============

@app.get("/budgets/{month}")
def get_budgets(month: str):
    """Get all budgets for a specific month"""
    budgets = budget_service.get_all_budgets(month)
    return {"budgets": budgets}

@app.put("/budgets/{month}")
def update_budgets(month: str, budget_update: BudgetUpdate):
    """Update budgets for a specific month"""
    try:
        budget_service.set_multiple_budgets(month, budget_update.budgets)
        return {"message": "Budgets updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/budgets/{month}/comparison")
def get_budget_comparison(month: str, exclude_recurring: bool = True):
    """Get budget vs actual comparison for a month (excludes recurring by default)"""
    # Get month start and end dates
    from datetime import datetime, timedelta
    month_date = datetime.strptime(month, "%Y-%m")
    month_start = month_date.replace(day=1)
    if month_date.month == 12:
        month_end = month_date.replace(year=month_date.year + 1, month=1, day=1)
    else:
        month_end = month_date.replace(month=month_date.month + 1, day=1)
    month_end = month_end - timedelta(days=1)

    # Get expenses and calculate comparison (excluding recurring for floating budget)
    df = expense_service.get_expenses(
        month_start.strftime("%Y-%m-%d"),
        month_end.strftime("%Y-%m-%d"),
        exclude_recurring
    )
    spending = expense_service.get_spending_by_category(df)
    comparison = budget_service.calculate_budget_comparison(month, spending)
    total_summary = budget_service.calculate_total_budget_summary(comparison)

    return {
        "comparison": comparison,
        "total_summary": total_summary
    }

# ============= Recurring Transactions =============

@app.get("/recurring")
def get_recurring_transactions():
    """Get all recurring transactions"""
    df = recurring_service.get_recurring_transactions()
    return {"recurring": df.to_dict(orient="records")}

@app.get("/recurring/active")
def get_active_recurring():
    """Get only active recurring transactions"""
    df = recurring_service.get_active_recurring_transactions()
    return {"recurring": df.to_dict(orient="records")}

@app.post("/recurring")
def add_recurring(recurring: RecurringCreate):
    """Add a new recurring transaction"""
    try:
        recurring_service.add_recurring_transaction(
            recurring.category,
            recurring.subcategory,
            recurring.amount,
            recurring.description
        )
        return {"message": "Recurring transaction added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/recurring/{recurring_id}")
def update_recurring(recurring_id: int, update: RecurringUpdate):
    """Update a recurring transaction"""
    try:
        recurring_service.toggle_recurring_active(recurring_id, update.is_active) if update.is_active is not None else None
        recurring_service.update_recurring_amount(recurring_id, update.amount) if update.amount is not None else None
        return {"message": "Recurring transaction updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/recurring/{recurring_id}")
def delete_recurring(recurring_id: int):
    """Delete a recurring transaction"""
    try:
        recurring_service.delete_recurring_transaction(recurring_id)
        return {"message": "Recurring transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recurring/status/{month}")
def get_recurring_status(month: str):
    """Get recurring transaction status for a month"""
    status = recurring_service.check_month_status(month)
    return {"status": status}

@app.post("/recurring/apply/{month}")
def apply_recurring(month: str):
    """Apply all pending recurring transactions for a month"""
    applied = recurring_service.apply_recurring_for_month(month)
    return {
        "message": f"Applied {len(applied)} recurring transactions",
        "applied": applied
    }

@app.get("/recurring/total")
def get_total_recurring():
    """Get total amount of active recurring transactions"""
    total = recurring_service.calculate_total_recurring_amount()
    return {"total": total}

# ============= Meal Planner Endpoints =============

# Recipe endpoints
@app.get("/recipes")
def get_recipes(category: Optional[str] = None):
    """Get all recipes, optionally filtered by category"""
    df = meal_service.get_recipes(category)
    return {"recipes": df.to_dict(orient="records")}

@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    """Get a single recipe by ID"""
    recipe = meal_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"recipe": recipe}

@app.post("/recipes")
def add_recipe(recipe: RecipeCreate):
    """Add a new recipe"""
    try:
        recipe_id = meal_service.add_recipe(
            recipe.name,
            recipe.category,
            recipe.ingredients,
            recipe.instructions,
            recipe.servings,
            recipe.prep_time,
            recipe.nutrition_info
        )
        return {"message": "Recipe added successfully", "recipe_id": recipe_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: RecipeUpdate):
    """Update an existing recipe"""
    try:
        meal_service.update_recipe(
            recipe_id,
            recipe.name,
            recipe.category,
            recipe.ingredients,
            recipe.instructions,
            recipe.servings,
            recipe.prep_time,
            recipe.nutrition_info
        )
        return {"message": "Recipe updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    """Delete a recipe"""
    try:
        meal_service.delete_recipe(recipe_id)
        return {"message": "Recipe deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Meal plan endpoints
@app.get("/meal-plans")
def get_meal_plans(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get meal plans, optionally filtered by date range"""
    df = meal_service.get_meal_plans(start_date, end_date)
    return {"meal_plans": df.to_dict(orient="records")}

@app.get("/meal-plans/{meal_plan_id}")
def get_meal_plan(meal_plan_id: int):
    """Get a single meal plan by ID"""
    meal_plan = meal_service.get_meal_plan_by_id(meal_plan_id)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return {"meal_plan": meal_plan}

@app.post("/meal-plans")
def add_meal_plan(meal_plan: MealPlanCreate):
    """Add a meal to the meal plan"""
    try:
        meal_plan_id = meal_service.add_meal_plan(
            meal_plan.date,
            meal_plan.meal_type,
            meal_plan.recipe_id,
            meal_plan.notes
        )
        return {"message": "Meal plan added successfully", "meal_plan_id": meal_plan_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/meal-plans/{meal_plan_id}")
def update_meal_plan(meal_plan_id: int, meal_plan: MealPlanUpdate):
    """Update an existing meal plan"""
    try:
        meal_service.update_meal_plan(
            meal_plan_id,
            meal_plan.date,
            meal_plan.meal_type,
            meal_plan.recipe_id,
            meal_plan.notes
        )
        return {"message": "Meal plan updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/meal-plans/{meal_plan_id}")
def delete_meal_plan(meal_plan_id: int):
    """Delete a meal plan"""
    try:
        meal_service.delete_meal_plan(meal_plan_id)
        return {"message": "Meal plan deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Grocery list endpoint
@app.get("/grocery-list")
def get_grocery_list(start_date: str, end_date: str):
    """Generate grocery list from meal plans in date range"""
    try:
        grocery_list = meal_service.generate_grocery_list(start_date, end_date)
        return {"grocery_list": grocery_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Meal plan statistics
@app.get("/meal-plans/stats")
def get_meal_plan_stats(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get meal plan statistics"""
    stats = meal_service.get_meal_plan_stats(start_date, end_date)
    return {"stats": stats}

# ============= Savings & Investment Endpoints (PLACEHOLDER) =============
# TODO: Implement savings and investment endpoints
# Planned routes:
#   GET    /savings/accounts - Get all savings accounts
#   POST   /savings/accounts - Create a savings account
#   GET    /investments - Get all investments
#   POST   /investments - Add an investment
#   GET    /net-worth - Calculate total net worth
#   GET    /portfolio/allocation - Get asset allocation

# ============= Journal Endpoints (PLACEHOLDER) =============
# TODO: Implement journaling endpoints
# Planned routes:
#   GET    /journal/entries - Get all journal entries
#   POST   /journal/entries - Create a journal entry
#   PUT    /journal/entries/{entry_id} - Update an entry
#   DELETE /journal/entries/{entry_id} - Delete an entry
#   GET    /journal/search - Search journal entries
#   GET    /journal/moods - Get mood statistics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
