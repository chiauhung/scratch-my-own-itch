'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  getMealPlans,
  getRecipes,
  addMealPlan,
  addRecipe,
  deleteMealPlan,
  deleteRecipe,
  getGroceryList
} from '@/lib/api'

interface Recipe {
  id: number
  name: string
  category: string
  ingredients: string
  instructions: string
  servings: number
  prep_time: number
  nutrition_info?: string
}

interface MealPlan {
  id: number
  date: string
  meal_type: string
  recipe_id: number
  recipe_name?: string
  notes: string
}

interface GroceryItem {
  ingredient: string
  count: number
}

export default function MealPlannerPage() {
  const [activeTab, setActiveTab] = useState<'planner' | 'recipes' | 'grocery'>('planner')
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([])
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [groceryList, setGroceryList] = useState<GroceryItem[]>([])
  const [selectedWeek, setSelectedWeek] = useState<string>(getCurrentWeekStart())
  const [loading, setLoading] = useState(false)

  // New meal plan form
  const [newMealDate, setNewMealDate] = useState('')
  const [newMealType, setNewMealType] = useState('breakfast')
  const [newMealRecipe, setNewMealRecipe] = useState('')
  const [newMealNotes, setNewMealNotes] = useState('')

  // New recipe form
  const [newRecipeName, setNewRecipeName] = useState('')
  const [newRecipeCategory, setNewRecipeCategory] = useState('main')
  const [newRecipeIngredients, setNewRecipeIngredients] = useState('')
  const [newRecipeInstructions, setNewRecipeInstructions] = useState('')
  const [newRecipeServings, setNewRecipeServings] = useState('4')
  const [newRecipePrepTime, setNewRecipePrepTime] = useState('30')

  function getCurrentWeekStart(): string {
    const today = new Date()
    const day = today.getDay()
    const diff = today.getDate() - day + (day === 0 ? -6 : 1) // Adjust to Monday
    const monday = new Date(today.setDate(diff))
    return monday.toISOString().split('T')[0]
  }

  function getWeekDates(startDate: string): string[] {
    const dates = []
    const start = new Date(startDate)
    for (let i = 0; i < 7; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      dates.push(date.toISOString().split('T')[0])
    }
    return dates
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
  }

  const loadMealPlans = async () => {
    setLoading(true)
    try {
      const data = await getMealPlans()
      setMealPlans(data)
    } catch (error) {
      console.error('Failed to load meal plans:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRecipes = async () => {
    setLoading(true)
    try {
      const data = await getRecipes()
      setRecipes(data)
    } catch (error) {
      console.error('Failed to load recipes:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadGroceryList = async () => {
    setLoading(true)
    try {
      const weekDates = getWeekDates(selectedWeek)
      const data = await getGroceryList(weekDates[0], weekDates[6])
      setGroceryList(data)
    } catch (error) {
      console.error('Failed to load grocery list:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMealPlans()
    loadRecipes()
  }, [])

  useEffect(() => {
    if (activeTab === 'grocery') {
      loadGroceryList()
    }
  }, [activeTab, selectedWeek])

  const handleAddMealPlan = async () => {
    if (!newMealDate || !newMealRecipe) return

    try {
      await addMealPlan({
        date: newMealDate,
        meal_type: newMealType,
        recipe_id: parseInt(newMealRecipe),
        notes: newMealNotes
      })
      setNewMealDate('')
      setNewMealType('breakfast')
      setNewMealRecipe('')
      setNewMealNotes('')
      loadMealPlans()
    } catch (error) {
      console.error('Failed to add meal plan:', error)
    }
  }

  const handleAddRecipe = async () => {
    if (!newRecipeName || !newRecipeIngredients) return

    try {
      await addRecipe({
        name: newRecipeName,
        category: newRecipeCategory,
        ingredients: newRecipeIngredients,
        instructions: newRecipeInstructions,
        servings: parseInt(newRecipeServings),
        prep_time: parseInt(newRecipePrepTime)
      })
      setNewRecipeName('')
      setNewRecipeCategory('main')
      setNewRecipeIngredients('')
      setNewRecipeInstructions('')
      setNewRecipeServings('4')
      setNewRecipePrepTime('30')
      loadRecipes()
    } catch (error) {
      console.error('Failed to add recipe:', error)
    }
  }

  const handleDeleteMealPlan = async (id: number) => {
    try {
      await deleteMealPlan(id)
      loadMealPlans()
    } catch (error) {
      console.error('Failed to delete meal plan:', error)
    }
  }

  const handleDeleteRecipe = async (id: number) => {
    try {
      await deleteRecipe(id)
      loadRecipes()
      loadMealPlans()
    } catch (error) {
      console.error('Failed to delete recipe:', error)
    }
  }

  const getMealsForDateAndType = (date: string, mealType: string): MealPlan[] => {
    return mealPlans.filter(mp => mp.date === date && mp.meal_type === mealType)
  }

  const weekDates = getWeekDates(selectedWeek)
  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack']

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50 p-8">
      <div className="container mx-auto max-w-7xl">
        {/* Back Button */}
        <Link href="/">
          <Button variant="outline" className="mb-6">
            ← Back to Dashboard
          </Button>
        </Link>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
            🍽️ Meal Planner
          </h1>
          <p className="text-lg text-gray-600">
            Plan your meals, manage recipes, and generate grocery lists
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('planner')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'planner'
                ? 'text-green-600 border-b-2 border-green-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Weekly Planner
          </button>
          <button
            onClick={() => setActiveTab('recipes')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'recipes'
                ? 'text-green-600 border-b-2 border-green-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Recipes
          </button>
          <button
            onClick={() => setActiveTab('grocery')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'grocery'
                ? 'text-green-600 border-b-2 border-green-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Grocery List
          </button>
        </div>

        {/* Weekly Planner Tab */}
        {activeTab === 'planner' && (
          <div className="space-y-6">
            {/* Week Selector */}
            <Card className="border-2 border-green-200 bg-white">
              <CardHeader>
                <CardTitle>Select Week</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <Button
                    onClick={() => {
                      const newDate = new Date(selectedWeek)
                      newDate.setDate(newDate.getDate() - 7)
                      setSelectedWeek(newDate.toISOString().split('T')[0])
                    }}
                  >
                    ← Previous Week
                  </Button>
                  <span className="font-semibold">
                    Week of {formatDate(selectedWeek)}
                  </span>
                  <Button
                    onClick={() => {
                      const newDate = new Date(selectedWeek)
                      newDate.setDate(newDate.getDate() + 7)
                      setSelectedWeek(newDate.toISOString().split('T')[0])
                    }}
                  >
                    Next Week →
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setSelectedWeek(getCurrentWeekStart())}
                  >
                    Current Week
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Add Meal Plan Form */}
            <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-white">
              <CardHeader>
                <CardTitle>Add Meal to Plan</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div>
                    <Label>Date</Label>
                    <Input
                      type="date"
                      value={newMealDate}
                      onChange={(e) => setNewMealDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Meal Type</Label>
                    <Select value={newMealType} onValueChange={setNewMealType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="breakfast">Breakfast</SelectItem>
                        <SelectItem value="lunch">Lunch</SelectItem>
                        <SelectItem value="dinner">Dinner</SelectItem>
                        <SelectItem value="snack">Snack</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Recipe</Label>
                    <Select value={newMealRecipe} onValueChange={setNewMealRecipe}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select recipe" />
                      </SelectTrigger>
                      <SelectContent>
                        {recipes.map((recipe) => (
                          <SelectItem key={recipe.id} value={recipe.id.toString()}>
                            {recipe.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Notes (Optional)</Label>
                    <Input
                      value={newMealNotes}
                      onChange={(e) => setNewMealNotes(e.target.value)}
                      placeholder="Special instructions..."
                    />
                  </div>
                  <div className="flex items-end">
                    <Button onClick={handleAddMealPlan} className="w-full bg-green-600 hover:bg-green-700">
                      Add Meal
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Weekly Calendar Grid */}
            <Card className="border-2 border-green-200 bg-white">
              <CardHeader>
                <CardTitle>Meal Plan Calendar</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr>
                        <th className="border border-gray-300 p-2 bg-gray-50 w-32">Meal Type</th>
                        {weekDates.map((date) => (
                          <th key={date} className="border border-gray-300 p-2 bg-gray-50 min-w-[150px]">
                            {formatDate(date)}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {mealTypes.map((mealType) => (
                        <tr key={mealType}>
                          <td className="border border-gray-300 p-2 font-semibold capitalize bg-green-50">
                            {mealType}
                          </td>
                          {weekDates.map((date) => {
                            const meals = getMealsForDateAndType(date, mealType)
                            return (
                              <td key={`${date}-${mealType}`} className="border border-gray-300 p-2 align-top">
                                {meals.length > 0 ? (
                                  <div className="space-y-2">
                                    {meals.map((meal) => (
                                      <div
                                        key={meal.id}
                                        className="bg-green-100 rounded p-2 text-sm relative group"
                                      >
                                        <div className="font-medium">{meal.recipe_name}</div>
                                        {meal.notes && (
                                          <div className="text-xs text-gray-600 mt-1">{meal.notes}</div>
                                        )}
                                        <button
                                          onClick={() => handleDeleteMealPlan(meal.id)}
                                          className="absolute top-1 right-1 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                          ✕
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                ) : (
                                  <div className="text-gray-400 text-sm">No meal planned</div>
                                )}
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Recipes Tab */}
        {activeTab === 'recipes' && (
          <div className="space-y-6">
            {/* Add Recipe Form */}
            <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-white">
              <CardHeader>
                <CardTitle>Add New Recipe</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label>Recipe Name</Label>
                      <Input
                        value={newRecipeName}
                        onChange={(e) => setNewRecipeName(e.target.value)}
                        placeholder="e.g., Chicken Stir Fry"
                      />
                    </div>
                    <div>
                      <Label>Category</Label>
                      <Select value={newRecipeCategory} onValueChange={setNewRecipeCategory}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="breakfast">Breakfast</SelectItem>
                          <SelectItem value="main">Main Dish</SelectItem>
                          <SelectItem value="side">Side Dish</SelectItem>
                          <SelectItem value="dessert">Dessert</SelectItem>
                          <SelectItem value="snack">Snack</SelectItem>
                          <SelectItem value="beverage">Beverage</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label>Servings</Label>
                        <Input
                          type="number"
                          value={newRecipeServings}
                          onChange={(e) => setNewRecipeServings(e.target.value)}
                        />
                      </div>
                      <div>
                        <Label>Prep Time (min)</Label>
                        <Input
                          type="number"
                          value={newRecipePrepTime}
                          onChange={(e) => setNewRecipePrepTime(e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                  <div>
                    <Label>Ingredients (one per line)</Label>
                    <textarea
                      className="w-full min-h-[100px] p-2 border rounded-md"
                      value={newRecipeIngredients}
                      onChange={(e) => setNewRecipeIngredients(e.target.value)}
                      placeholder="2 cups rice&#10;1 lb chicken&#10;1 onion, diced"
                    />
                  </div>
                  <div>
                    <Label>Instructions</Label>
                    <textarea
                      className="w-full min-h-[100px] p-2 border rounded-md"
                      value={newRecipeInstructions}
                      onChange={(e) => setNewRecipeInstructions(e.target.value)}
                      placeholder="1. Heat oil in pan&#10;2. Cook chicken until golden..."
                    />
                  </div>
                  <Button onClick={handleAddRecipe} className="bg-green-600 hover:bg-green-700">
                    Add Recipe
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recipe List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recipes.map((recipe) => (
                <Card key={recipe.id} className="border-2 border-green-200 hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-xl">{recipe.name}</CardTitle>
                        <CardDescription className="capitalize">{recipe.category}</CardDescription>
                      </div>
                      <button
                        onClick={() => handleDeleteRecipe(recipe.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        ✕
                      </button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 text-sm">
                      <div className="flex gap-4 text-gray-600">
                        <span>🍽️ {recipe.servings} servings</span>
                        <span>⏱️ {recipe.prep_time} min</span>
                      </div>
                      <div>
                        <div className="font-semibold text-gray-700 mb-1">Ingredients:</div>
                        <div className="text-gray-600 whitespace-pre-line text-xs">
                          {recipe.ingredients}
                        </div>
                      </div>
                      {recipe.instructions && (
                        <div>
                          <div className="font-semibold text-gray-700 mb-1">Instructions:</div>
                          <div className="text-gray-600 whitespace-pre-line text-xs">
                            {recipe.instructions}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
              {recipes.length === 0 && (
                <div className="col-span-3 text-center text-gray-500 py-8">
                  No recipes yet. Add your first recipe above!
                </div>
              )}
            </div>
          </div>
        )}

        {/* Grocery List Tab */}
        {activeTab === 'grocery' && (
          <div className="space-y-6">
            <Card className="border-2 border-green-200 bg-white">
              <CardHeader>
                <CardTitle>Grocery List for Week of {formatDate(selectedWeek)}</CardTitle>
                <CardDescription>
                  Automatically generated from your meal plan
                </CardDescription>
              </CardHeader>
              <CardContent>
                {groceryList.length > 0 ? (
                  <div className="space-y-2">
                    {groceryList.map((item, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 bg-green-50 rounded">
                        <input type="checkbox" className="w-5 h-5" />
                        <span className="flex-1">{item.ingredient}</span>
                        <span className="text-gray-600 text-sm">
                          (appears in {item.count} {item.count === 1 ? 'meal' : 'meals'})
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    No meals planned for this week. Add some meals to generate a grocery list!
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
