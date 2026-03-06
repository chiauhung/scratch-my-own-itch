/**
 * API Client for Expense Tracker
 * Connects to FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Expense {
  id: number;
  date: string;
  category: string;
  subcategory: string;
  amount: number;
  description: string;
  is_recurring?: number;
}

export interface RecurringTransaction {
  id: number;
  category: string;
  subcategory: string;
  amount: number;
  description: string;
  is_active: number;
}

export interface BudgetComparison {
  budget: number;
  spent: number;
  remaining: number;
  percentage: number;
}

export interface MonthOption {
  value: string;  // e.g., "2025-10"
  display: string;  // e.g., "October 25"
}

// Helper function for API calls
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.statusText}`);
  }

  return response.json();
}

// ============= Config =============

export const getCategories = () =>
  apiCall<{ categories: Record<string, string[]> }>('/config/categories');

export const getDefaultBudgets = () =>
  apiCall<{ budgets: Record<string, number> }>('/config/default-budgets');

// ============= Expenses =============

export const getExpenses = (startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{ expenses: Expense[] }>(`/expenses${query}`);
};

export const addExpense = (expense: Omit<Expense, 'id'>) =>
  apiCall<{ message: string }>('/expenses', {
    method: 'POST',
    body: JSON.stringify(expense),
  });

export const deleteExpense = (id: number) =>
  apiCall<{ message: string }>(`/expenses/${id}`, { method: 'DELETE' });

export const updateExpense = (id: number, expense: Omit<Expense, 'id'>) =>
  apiCall<{ message: string }>(`/expenses/${id}`, {
    method: 'PUT',
    body: JSON.stringify(expense),
  });

export const getExpenseSummary = (startDate?: string, endDate?: string, excludeRecurring: boolean = true) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (excludeRecurring) params.append('exclude_recurring', 'true');
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{ summary: any }>(`/expenses/summary${query}`);
};

export const getSpendingByCategory = (startDate?: string, endDate?: string, excludeRecurring: boolean = true) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (excludeRecurring) params.append('exclude_recurring', 'true');
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{ spending: Record<string, number> }>(`/expenses/by-category${query}`);
};

export const getSpendingBySubcategory = (startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{ spending: Array<{ category: string; subcategory: string; total: number }> }>(`/expenses/by-subcategory${query}`);
};

export const getDailySpending = (startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{ daily: Array<{ date: string; amount: number }> }>(`/expenses/daily${query}`);
};

export const getAvailableMonths = () =>
  apiCall<{ months: MonthOption[] }>('/expenses/available-months');

// ============= Budgets =============

export const getBudgets = (month: string) =>
  apiCall<{ budgets: Record<string, number> }>(`/budgets/${month}`);

export const updateBudgets = (month: string, budgets: Record<string, number>) =>
  apiCall<{ message: string }>(`/budgets/${month}`, {
    method: 'PUT',
    body: JSON.stringify({ budgets }),
  });

export const getBudgetComparison = (month: string, excludeRecurring: boolean = true) => {
  const params = new URLSearchParams();
  if (excludeRecurring) params.append('exclude_recurring', 'true');
  else params.append('exclude_recurring', 'false');
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{
    comparison: Record<string, BudgetComparison>;
    total_summary: any;
  }>(`/budgets/${month}/comparison${query}`);
};

// ============= Recurring =============

export const getRecurringTransactions = () =>
  apiCall<{ recurring: RecurringTransaction[] }>('/recurring');

export const getActiveRecurring = () =>
  apiCall<{ recurring: RecurringTransaction[] }>('/recurring/active');

export const addRecurring = (data: Omit<RecurringTransaction, 'id' | 'is_active'>) =>
  apiCall<{ message: string }>('/recurring', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const updateRecurring = (
  id: number,
  data: { amount?: number; is_active?: boolean }
) =>
  apiCall<{ message: string }>(`/recurring/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

export const deleteRecurring = (id: number) =>
  apiCall<{ message: string }>(`/recurring/${id}`, { method: 'DELETE' });

export const getRecurringStatus = (month: string) =>
  apiCall<{
    status: {
      total_recurring: number;
      applied: number;
      pending: number;
      total_amount: number;
      applied_amount: number;
      pending_amount: number;
    };
  }>(`/recurring/status/${month}`);

export const applyRecurring = (month: string) =>
  apiCall<{ message: string; applied: any[] }>(`/recurring/apply/${month}`, {
    method: 'POST',
  });

// ============= Meal Planner =============

export interface Recipe {
  id: number;
  name: string;
  category: string;
  ingredients: string;
  instructions: string;
  servings: number;
  prep_time: number;
  nutrition_info?: string;
}

export interface MealPlan {
  id: number;
  date: string;
  meal_type: string;
  recipe_id: number;
  recipe_name: string;
  recipe_category: string;
  notes: string;
}

export interface GroceryItem {
  ingredient: string;
  count: number;
}

// Recipe endpoints
export const getRecipes = async (category?: string): Promise<Recipe[]> => {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  const query = params.toString() ? `?${params}` : '';
  const response = await apiCall<{ recipes: Recipe[] }>(`/recipes${query}`);
  return response.recipes;
};

export const getRecipe = async (id: number): Promise<Recipe> => {
  const response = await apiCall<{ recipe: Recipe }>(`/recipes/${id}`);
  return response.recipe;
};

export const addRecipe = (recipe: Omit<Recipe, 'id'>) =>
  apiCall<{ message: string; recipe_id: number }>('/recipes', {
    method: 'POST',
    body: JSON.stringify(recipe),
  });

export const updateRecipe = (id: number, recipe: Partial<Omit<Recipe, 'id'>>) =>
  apiCall<{ message: string }>(`/recipes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(recipe),
  });

export const deleteRecipe = (id: number) =>
  apiCall<{ message: string }>(`/recipes/${id}`, { method: 'DELETE' });

// Meal plan endpoints
export const getMealPlans = async (startDate?: string, endDate?: string): Promise<MealPlan[]> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString() ? `?${params}` : '';
  const response = await apiCall<{ meal_plans: MealPlan[] }>(`/meal-plans${query}`);
  return response.meal_plans;
};

export const getMealPlan = async (id: number): Promise<MealPlan> => {
  const response = await apiCall<{ meal_plan: MealPlan }>(`/meal-plans/${id}`);
  return response.meal_plan;
};

export const addMealPlan = (mealPlan: Omit<MealPlan, 'id' | 'recipe_name' | 'recipe_category'>) =>
  apiCall<{ message: string; meal_plan_id: number }>('/meal-plans', {
    method: 'POST',
    body: JSON.stringify(mealPlan),
  });

export const updateMealPlan = (id: number, mealPlan: Partial<Omit<MealPlan, 'id' | 'recipe_name' | 'recipe_category'>>) =>
  apiCall<{ message: string }>(`/meal-plans/${id}`, {
    method: 'PUT',
    body: JSON.stringify(mealPlan),
  });

export const deleteMealPlan = (id: number) =>
  apiCall<{ message: string }>(`/meal-plans/${id}`, { method: 'DELETE' });

// Grocery list endpoint
export const getGroceryList = async (startDate: string, endDate: string): Promise<GroceryItem[]> => {
  const params = new URLSearchParams();
  params.append('start_date', startDate);
  params.append('end_date', endDate);
  const response = await apiCall<{ grocery_list: GroceryItem[] }>(`/grocery-list?${params}`);
  return response.grocery_list;
};

// Meal plan statistics
export const getMealPlanStats = (startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString() ? `?${params}` : '';
  return apiCall<{
    stats: {
      total_meals: number;
      by_meal_type: Record<string, number>;
      by_category: Record<string, number>;
      unique_recipes: number;
    };
  }>(`/meal-plans/stats${query}`);
};
