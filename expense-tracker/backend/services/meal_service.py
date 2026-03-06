"""
Meal Service - Business logic for meal planning and recipe management
"""

import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
from database.sqlite_impl import SQLiteDatabase


class MealService:
    """Service for managing meal plans and recipes"""

    def __init__(self, db: SQLiteDatabase):
        self.db = db
        self._ensure_tables()

    def _ensure_tables(self):
        """Create meal planner tables if they don't exist"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Recipes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT,
                servings INTEGER DEFAULT 4,
                prep_time INTEGER DEFAULT 30,
                nutrition_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Meal plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                recipe_id INTEGER NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )
        """)

        conn.commit()
        conn.close()

    # ============= Recipe Management =============

    def add_recipe(
        self,
        name: str,
        category: str,
        ingredients: str,
        instructions: str = "",
        servings: int = 4,
        prep_time: int = 30,
        nutrition_info: Optional[str] = None
    ):
        """Add a new recipe"""
        if not name or not ingredients:
            raise ValueError("Recipe name and ingredients are required")

        valid_categories = ['breakfast', 'main', 'side', 'dessert', 'snack', 'beverage']
        if category not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")

        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO recipes (name, category, ingredients, instructions, servings, prep_time, nutrition_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, category, ingredients, instructions, servings, prep_time, nutrition_info)
        )

        recipe_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return recipe_id

    def get_recipes(self, category: Optional[str] = None) -> pd.DataFrame:
        """Get all recipes, optionally filtered by category"""
        conn = self.db._get_connection()

        if category:
            df = pd.read_sql_query(
                "SELECT * FROM recipes WHERE category = ? ORDER BY name",
                conn,
                params=(category,)
            )
        else:
            df = pd.read_sql_query(
                "SELECT * FROM recipes ORDER BY category, name",
                conn
            )

        conn.close()
        return df

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict]:
        """Get a single recipe by ID"""
        conn = self.db._get_connection()

        df = pd.read_sql_query(
            "SELECT * FROM recipes WHERE id = ?",
            conn,
            params=(recipe_id,)
        )

        conn.close()

        if df.empty:
            return None
        return df.iloc[0].to_dict()

    def update_recipe(
        self,
        recipe_id: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
        ingredients: Optional[str] = None,
        instructions: Optional[str] = None,
        servings: Optional[int] = None,
        prep_time: Optional[int] = None,
        nutrition_info: Optional[str] = None
    ):
        """Update an existing recipe"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if ingredients is not None:
            updates.append("ingredients = ?")
            params.append(ingredients)
        if instructions is not None:
            updates.append("instructions = ?")
            params.append(instructions)
        if servings is not None:
            updates.append("servings = ?")
            params.append(servings)
        if prep_time is not None:
            updates.append("prep_time = ?")
            params.append(prep_time)
        if nutrition_info is not None:
            updates.append("nutrition_info = ?")
            params.append(nutrition_info)

        if not updates:
            return

        params.append(recipe_id)
        query = f"UPDATE recipes SET {', '.join(updates)} WHERE id = ?"

        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def delete_recipe(self, recipe_id: int):
        """Delete a recipe and associated meal plans"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # First delete associated meal plans
        cursor.execute("DELETE FROM meal_plans WHERE recipe_id = ?", (recipe_id,))
        # Then delete the recipe
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))

        conn.commit()
        conn.close()

    # ============= Meal Plan Management =============

    def add_meal_plan(
        self,
        date: str,
        meal_type: str,
        recipe_id: int,
        notes: str = ""
    ):
        """Add a meal to the meal plan"""
        # Validate meal type
        valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        if meal_type not in valid_meal_types:
            raise ValueError(f"Meal type must be one of: {', '.join(valid_meal_types)}")

        # Validate recipe exists
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe with ID {recipe_id} not found")

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO meal_plans (date, meal_type, recipe_id, notes)
            VALUES (?, ?, ?, ?)
            """,
            (date, meal_type, recipe_id, notes)
        )

        meal_plan_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return meal_plan_id

    def get_meal_plans(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Get meal plans, optionally filtered by date range"""
        query = """
            SELECT
                mp.id,
                mp.date,
                mp.meal_type,
                mp.recipe_id,
                r.name as recipe_name,
                r.category as recipe_category,
                mp.notes,
                mp.created_at
            FROM meal_plans mp
            JOIN recipes r ON mp.recipe_id = r.id
        """

        params = []
        conditions = []

        if start_date:
            conditions.append("mp.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("mp.date <= ?")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY mp.date, mp.meal_type"

        conn = self.db._get_connection()
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()

        return df

    def get_meal_plan_by_id(self, meal_plan_id: int) -> Optional[Dict]:
        """Get a single meal plan by ID"""
        conn = self.db._get_connection()

        df = pd.read_sql_query(
            """
            SELECT
                mp.id,
                mp.date,
                mp.meal_type,
                mp.recipe_id,
                r.name as recipe_name,
                mp.notes
            FROM meal_plans mp
            JOIN recipes r ON mp.recipe_id = r.id
            WHERE mp.id = ?
            """,
            conn,
            params=(meal_plan_id,)
        )

        conn.close()

        if df.empty:
            return None
        return df.iloc[0].to_dict()

    def update_meal_plan(
        self,
        meal_plan_id: int,
        date: Optional[str] = None,
        meal_type: Optional[str] = None,
        recipe_id: Optional[int] = None,
        notes: Optional[str] = None
    ):
        """Update an existing meal plan"""
        updates = []
        params = []

        if date is not None:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
            updates.append("date = ?")
            params.append(date)

        if meal_type is not None:
            valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
            if meal_type not in valid_meal_types:
                raise ValueError(f"Meal type must be one of: {', '.join(valid_meal_types)}")
            updates.append("meal_type = ?")
            params.append(meal_type)

        if recipe_id is not None:
            recipe = self.get_recipe_by_id(recipe_id)
            if not recipe:
                raise ValueError(f"Recipe with ID {recipe_id} not found")
            updates.append("recipe_id = ?")
            params.append(recipe_id)

        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)

        if not updates:
            return

        params.append(meal_plan_id)
        query = f"UPDATE meal_plans SET {', '.join(updates)} WHERE id = ?"

        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def delete_meal_plan(self, meal_plan_id: int):
        """Delete a meal plan"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM meal_plans WHERE id = ?", (meal_plan_id,))
        conn.commit()
        conn.close()

    # ============= Grocery List Generation =============

    def generate_grocery_list(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, any]]:
        """Generate grocery list from meal plans in date range"""
        # Get all meal plans in range
        meal_plans = self.get_meal_plans(start_date, end_date)

        if meal_plans.empty:
            return []

        # Get unique recipe IDs
        recipe_ids = meal_plans['recipe_id'].unique().tolist()

        # Get all recipes
        conn = self.db._get_connection()
        placeholders = ','.join('?' * len(recipe_ids))
        recipes_df = pd.read_sql_query(
            f"SELECT id, ingredients FROM recipes WHERE id IN ({placeholders})",
            conn,
            params=recipe_ids
        )
        conn.close()

        # Parse ingredients and count occurrences
        ingredient_count = {}

        for _, recipe in recipes_df.iterrows():
            recipe_id = recipe['id']
            ingredients = recipe['ingredients']

            # Count how many times this recipe appears in the meal plan
            recipe_count = len(meal_plans[meal_plans['recipe_id'] == recipe_id])

            # Parse ingredients (one per line)
            ingredient_lines = [line.strip() for line in ingredients.split('\n') if line.strip()]

            for ingredient in ingredient_lines:
                if ingredient in ingredient_count:
                    ingredient_count[ingredient] += recipe_count
                else:
                    ingredient_count[ingredient] = recipe_count

        # Convert to list of dictionaries
        grocery_list = [
            {'ingredient': ingredient, 'count': count}
            for ingredient, count in sorted(ingredient_count.items())
        ]

        return grocery_list

    # ============= Statistics =============

    def get_meal_plan_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """Get statistics about meal plans"""
        meal_plans = self.get_meal_plans(start_date, end_date)

        if meal_plans.empty:
            return {
                'total_meals': 0,
                'by_meal_type': {},
                'by_category': {},
                'unique_recipes': 0
            }

        return {
            'total_meals': len(meal_plans),
            'by_meal_type': meal_plans['meal_type'].value_counts().to_dict(),
            'by_category': meal_plans['recipe_category'].value_counts().to_dict(),
            'unique_recipes': meal_plans['recipe_id'].nunique()
        }
