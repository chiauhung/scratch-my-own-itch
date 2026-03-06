'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import {
  getCategories,
  getExpenses,
  addExpense,
  deleteExpense,
  updateExpense,
  getExpenseSummary,
  getSpendingByCategory,
  getSpendingBySubcategory,
  getDailySpending,
  getBudgets,
  updateBudgets,
  getBudgetComparison,
  getRecurringTransactions,
  addRecurring,
  updateRecurring,
  deleteRecurring,
  getRecurringStatus,
  applyRecurring,
  getAvailableMonths,
  type Expense,
  type RecurringTransaction,
  type MonthOption,
} from '@/lib/api'
import { formatCurrency, formatDate, toDateInputValue, getCurrentMonth, getMonthDates, cn } from '@/lib/utils'
import { NestedPieChart } from '@/components/NestedPieChart'
import { LineChart } from '@/components/LineChart'

type Tab = 'dashboard' | 'add' | 'budget' | 'recurring' | 'history'

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')
  const [categories, setCategories] = useState<Record<string, string[]>>({})
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [spending, setSpending] = useState<Record<string, number>>({})
  const [subcategorySpending, setSubcategorySpending] = useState<Array<{ category: string; subcategory: string; total: number }>>([])
  const [daily, setDaily] = useState<Array<{ date: string; amount: number }>>([])
  const [loading, setLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)

  // Add Expense form state
  const [newExpense, setNewExpense] = useState({
    date: new Date().toISOString().split('T')[0],
    category: '',
    subcategory: '',
    amount: '',
    description: ''
  })

  // Global month selector
  const [selectedMonth, setSelectedMonth] = useState(getCurrentMonth())
  const [availableMonths, setAvailableMonths] = useState<MonthOption[]>([])

  // Budget state
  const [budgets, setBudgets] = useState<Record<string, number>>({})
  const [budgetComparison, setBudgetComparison] = useState<any>(null)
  const [fullBudgetComparison, setFullBudgetComparison] = useState<any>(null)
  const [editingBudgets, setEditingBudgets] = useState<Record<string, string>>({})

  // Recurring state
  const [recurring, setRecurring] = useState<RecurringTransaction[]>([])
  const [recurringStatus, setRecurringStatus] = useState<any>(null)
  const [newRecurring, setNewRecurring] = useState({
    category: '',
    subcategory: '',
    amount: '',
    description: 'Recurring monthly expense'
  })

  // Edit expense state
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null)

  // Calculator state
  const [calcDisplay, setCalcDisplay] = useState('0')
  const [calcValue, setCalcValue] = useState<number | null>(null)
  const [calcOperation, setCalcOperation] = useState<string | null>(null)
  const [calcNewNumber, setCalcNewNumber] = useState(true)

  // Pagination state for History tab
  const [currentPage, setCurrentPage] = useState(1)
  const rowsPerPage = 50

  useEffect(() => {
    fetchAllData()
  }, [refreshKey, selectedMonth])

  // Reset pagination when switching to history tab
  useEffect(() => {
    if (activeTab === 'history') {
      setCurrentPage(1)
    }
  }, [activeTab])

  async function fetchAllData() {
    try {
      // Get date range for selected month
      const monthDates = getMonthDates(selectedMonth)

      const [categoriesRes, monthsRes, expensesRes, summaryRes, spendingRes, subcategoryRes, dailyRes, budgetsRes, comparisonRes, fullComparisonRes, recurringRes, statusRes] = await Promise.all([
        getCategories(),
        getAvailableMonths(),
        getExpenses(monthDates.start, monthDates.end), // Filter expenses by selected month for History tab
        getExpenseSummary(monthDates.start, monthDates.end, true), // Exclude recurring for score cards (floating only)
        getSpendingByCategory(monthDates.start, monthDates.end, false), // Include ALL expenses (including recurring) for pie chart
        getSpendingBySubcategory(monthDates.start, monthDates.end), // Get subcategory data for nested chart
        getDailySpending(monthDates.start, monthDates.end), // Excludes recurring by default for trend analysis
        getBudgets(selectedMonth),
        getBudgetComparison(selectedMonth, true),  // Exclude recurring for floating budget comparison
        getBudgetComparison(selectedMonth, false), // Include recurring for budget tab
        getRecurringTransactions(),
        getRecurringStatus(selectedMonth),
      ])

      setCategories(categoriesRes.categories)
      setAvailableMonths(monthsRes.months)
      setExpenses(expensesRes.expenses)
      setSummary(summaryRes.summary)
      setSpending(spendingRes.spending)
      setSubcategorySpending(subcategoryRes.spending)
      setDaily(dailyRes.daily)
      setBudgets(budgetsRes.budgets)
      setBudgetComparison(comparisonRes)
      setFullBudgetComparison(fullComparisonRes)
      setRecurring(recurringRes.recurring)
      setRecurringStatus(statusRes.status)

      // Initialize new expense category to Food (Essential Living) if not set
      if (!newExpense.category && Object.keys(categoriesRes.categories).length > 0) {
        const defaultCategory = '生活必要支出 (Essential Living)'
        const defaultSubcategory = 'Food'
        setNewExpense(prev => ({
          ...prev,
          category: defaultCategory,
          subcategory: defaultSubcategory
        }))
      }

      // Initialize new recurring category if not set
      if (!newRecurring.category && Object.keys(categoriesRes.categories).length > 0) {
        const firstCategory = Object.keys(categoriesRes.categories)[0]
        setNewRecurring(prev => ({
          ...prev,
          category: firstCategory,
          subcategory: categoriesRes.categories[firstCategory][0]
        }))
      }

      // Initialize editing budgets
      const initialEditBudgets: Record<string, string> = {}
      Object.entries(budgetsRes.budgets).forEach(([cat, amt]) => {
        initialEditBudgets[cat] = amt.toString()
      })
      setEditingBudgets(initialEditBudgets)

    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleAddExpense(e: React.FormEvent) {
    e.preventDefault()
    try {
      await addExpense({
        date: newExpense.date,
        category: newExpense.category,
        subcategory: newExpense.subcategory,
        amount: parseFloat(newExpense.amount),
        description: newExpense.description,
        id: 0
      })
      setNewExpense({
        date: new Date().toISOString().split('T')[0],
        category: newExpense.category,
        subcategory: categories[newExpense.category][0],
        amount: '',
        description: ''
      })
      setRefreshKey(k => k + 1)
      setActiveTab('history')
    } catch (error: any) {
      alert(error.message)
    }
  }

  async function handleDeleteExpense(id: number) {
    if (confirm('Delete this expense?')) {
      try {
        await deleteExpense(id)
        setRefreshKey(k => k + 1)
      } catch (error: any) {
        alert(error.message)
      }
    }
  }

  async function handleEditExpense(expense: Expense) {
    setEditingExpense(expense)
  }

  async function handleUpdateExpense(e: React.FormEvent) {
    e.preventDefault()
    if (!editingExpense) return

    try {
      await updateExpense(editingExpense.id, {
        date: editingExpense.date,
        category: editingExpense.category,
        subcategory: editingExpense.subcategory,
        amount: editingExpense.amount,
        description: editingExpense.description
      })
      setEditingExpense(null)
      setRefreshKey(k => k + 1)
    } catch (error: any) {
      alert(error.message)
    }
  }

  async function handleSaveBudgets() {
    try {
      const budgetValues: Record<string, number> = {}
      Object.entries(editingBudgets).forEach(([cat, val]) => {
        budgetValues[cat] = parseFloat(val)
      })
      await updateBudgets(selectedMonth, budgetValues)
      setRefreshKey(k => k + 1)
      alert('Budgets updated!')
    } catch (error: any) {
      alert(error.message)
    }
  }

  async function handleAddRecurring(e: React.FormEvent) {
    e.preventDefault()
    try {
      await addRecurring({
        category: newRecurring.category,
        subcategory: newRecurring.subcategory,
        amount: parseFloat(newRecurring.amount),
        description: newRecurring.description
      })
      setNewRecurring({
        category: newRecurring.category,
        subcategory: categories[newRecurring.category][0],
        amount: '',
        description: 'Recurring monthly expense'
      })
      setRefreshKey(k => k + 1)
    } catch (error: any) {
      alert(error.message)
    }
  }

  async function handleToggleRecurring(id: number, isActive: boolean) {
    try {
      await updateRecurring(id, { is_active: !isActive })
      setRefreshKey(k => k + 1)
    } catch (error: any) {
      alert(error.message)
    }
  }

  async function handleDeleteRecurring(id: number) {
    if (confirm('Delete this recurring transaction?')) {
      try {
        await deleteRecurring(id)
        setRefreshKey(k => k + 1)
      } catch (error: any) {
        alert(error.message)
      }
    }
  }

  async function handleApplyRecurring() {
    try {
      const result = await applyRecurring(selectedMonth)
      alert(result.message)
      setRefreshKey(k => k + 1)
    } catch (error: any) {
      alert(error.message)
    }
  }

  // Calculator functions
  function handleCalcNumber(num: string) {
    if (calcNewNumber) {
      setCalcDisplay(num)
      setCalcNewNumber(false)
    } else {
      setCalcDisplay(calcDisplay === '0' ? num : calcDisplay + num)
    }
  }

  function handleCalcOperation(op: string) {
    const currentValue = parseFloat(calcDisplay)

    if (calcValue === null) {
      setCalcValue(currentValue)
    } else if (calcOperation) {
      const newValue = calculateResult(calcValue, currentValue, calcOperation)
      setCalcDisplay(newValue.toString())
      setCalcValue(newValue)
    }

    setCalcOperation(op)
    setCalcNewNumber(true)
  }

  function handleCalcEquals() {
    if (calcValue !== null && calcOperation) {
      const currentValue = parseFloat(calcDisplay)
      const result = calculateResult(calcValue, currentValue, calcOperation)
      setCalcDisplay(result.toString())
      setCalcValue(null)
      setCalcOperation(null)
      setCalcNewNumber(true)
    }
  }

  function handleCalcClear() {
    setCalcDisplay('0')
    setCalcValue(null)
    setCalcOperation(null)
    setCalcNewNumber(true)
  }

  function handleCalcDecimal() {
    if (calcNewNumber) {
      setCalcDisplay('0.')
      setCalcNewNumber(false)
    } else if (!calcDisplay.includes('.')) {
      setCalcDisplay(calcDisplay + '.')
    }
  }

  function calculateResult(a: number, b: number, op: string): number {
    switch (op) {
      case '+': return a + b
      case '-': return a - b
      case '*': return a * b
      case '/': return b !== 0 ? a / b : 0
      default: return b
    }
  }

  function handleUseCalcResult() {
    const value = parseFloat(calcDisplay)
    if (!isNaN(value)) {
      setNewExpense({ ...newExpense, amount: value.toFixed(2) })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="heading-section text-xl animate-pulse">Loading your expenses... ✨</div>
      </div>
    )
  }

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'add', label: 'Add Expense', icon: '➕' },
    { id: 'budget', label: 'Budget', icon: '💰' },
    { id: 'recurring', label: 'Recurring', icon: '🔁' },
    { id: 'history', label: 'History', icon: '📝' },
  ]

  return (
    <div className="space-y-6">
      {/* Header with Month Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold heading-main">💰 Expense Tracker</h1>
          <p className="text-sm text-muted-custom mt-1">Track your spending and manage your budget</p>
        </div>
        <div className="flex items-center space-x-3">
          <Label className="text-sm font-medium heading-section">Month:</Label>
          <Select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="w-44"
          >
            {availableMonths.map(month => (
              <option key={month.value} value={month.value}>
                {month.display}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex space-x-2 border-b border-theme-medium pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "px-4 py-2 rounded-t-lg font-medium transition-all",
              activeTab === tab.id
                ? "bg-primary text-primary-foreground shadow-md"
                : "bg-white/60 heading-section hover:bg-pastel-lavender/30"
            )}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Summary Cards - Only 3 cards, removed Highest */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Expenses (Floating)</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-number">
                  {formatCurrency(summary?.total || 0)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Average/Day</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-number">
                  {formatCurrency(summary?.average || 0)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Transactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-number">
                  {summary?.count || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Spending by Category - NESTED PIE CHART */}
            <Card>
              <CardHeader>
                <CardTitle>🥧 Spending Breakdown</CardTitle>
                <CardDescription>Double-layer view: categories (inner) and subcategories (outer)</CardDescription>
              </CardHeader>
              <CardContent>
                <NestedPieChart
                  data={subcategorySpending}
                  categoryColors={{
                    '固定支出 (Fixed Expenses)': '#BDE0FE',
                    '生活必要支出 (Essential Living)': '#FFC8DD',
                    '生活质量支出 (Quality of Life)': '#FFAFCC',
                    '基金 (Fund/Savings)': '#D8F7F2',
                  }}
                />
              </CardContent>
            </Card>

            {/* Budget Overview - READ ONLY */}
            <Card>
              <CardHeader>
                <CardTitle>💰 Floating Budget</CardTitle>
                <CardDescription>Budget excluding fixed recurring expenses</CardDescription>
              </CardHeader>
              <CardContent>
                {budgetComparison && recurringStatus && fullBudgetComparison ? (
                  <div className="space-y-4">
                    {/* Total Summary - Floating Budget */}
                    <div className="p-4 bg-theme-surface rounded-lg space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-body">Floating Budget:</span>
                        <span className="font-bold text-number">
                          {formatCurrency(budgetComparison.total_summary.total_budget - recurringStatus.total_amount)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-body">Floating Spent:</span>
                        <span className="font-bold text-number">
                          {formatCurrency(budgetComparison.total_summary.total_spent)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-body">Remaining:</span>
                        <span className={cn(
                          "font-bold",
                          ((budgetComparison.total_summary.total_budget - recurringStatus.total_amount) - budgetComparison.total_summary.total_spent) >= 0 ? "text-blue-600" : "text-red-600"
                        )}>
                          {formatCurrency((budgetComparison.total_summary.total_budget - recurringStatus.total_amount) - budgetComparison.total_summary.total_spent)}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs text-muted-custom pt-2 border-t border-theme-light">
                        <span>Fixed Recurring/month:</span>
                        <span className="font-semibold">
                          {formatCurrency(recurringStatus.total_amount)}
                        </span>
                      </div>
                    </div>

                    {/* Category Breakdowns - Using Full Budget Data */}
                    <div className="space-y-3">
                      {Object.entries(fullBudgetComparison.comparison).map(([category, data]: [string, any]) => {
                        const percentage = data.percentage
                        const isOver = percentage > 100

                        return (
                          <div key={category} className="space-y-1">
                            <div className="flex justify-between items-center text-xs">
                              <span className="font-medium heading-section">{category}</span>
                              <span className={cn(
                                "font-semibold",
                                isOver ? "text-red-600" : percentage > 80 ? "text-yellow-600" : "text-number"
                              )}>
                                {percentage.toFixed(0)}%
                              </span>
                            </div>
                            <div className="w-full bg-theme-surface rounded-full h-2">
                              <div
                                className={cn(
                                  "h-2 rounded-full transition-all",
                                  isOver ? "bg-gradient-to-r from-red-400 to-red-600" :
                                  percentage > 80 ? "bg-gradient-to-r from-yellow-400 to-yellow-600" :
                                  "bg-gradient-to-r from-blue-400 to-blue-600"
                                )}
                                style={{ width: `${Math.min(percentage, 100)}%` }}
                              />
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    {/* Link to Budget Tab */}
                    <button
                      onClick={() => setActiveTab('budget')}
                      className="w-full mt-4 text-sm text-description hover:heading-card font-medium underline transition-colors"
                    >
                      View detailed budget →
                    </button>
                  </div>
                ) : (
                  <p className="text-sm text-muted-custom">Loading budget data...</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Daily Spending Trend */}
          <Card>
            <CardHeader>
              <CardTitle>📈 Daily Spending Trend</CardTitle>
              <CardDescription>Your spending pattern for the selected month (excludes recurring expenses)</CardDescription>
            </CardHeader>
            <CardContent>
              <LineChart data={daily.slice(0, 30).reverse()} height={250} />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Add Expense Tab */}
      {activeTab === 'add' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form - 2/3 width */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>➕ Add New Expense</CardTitle>
              <CardDescription>Track your spending by adding a new expense</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddExpense} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date">Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={newExpense.date}
                    onChange={(e) => setNewExpense({ ...newExpense, date: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="amount">Amount (RM)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={newExpense.amount}
                    onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select
                    id="category"
                    value={newExpense.category}
                    onChange={(e) => setNewExpense({
                      ...newExpense,
                      category: e.target.value,
                      subcategory: categories[e.target.value]?.[0] || ''
                    })}
                    required
                  >
                    {Object.keys(categories).map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="subcategory">Subcategory</Label>
                  <Select
                    id="subcategory"
                    value={newExpense.subcategory}
                    onChange={(e) => setNewExpense({ ...newExpense, subcategory: e.target.value })}
                    required
                  >
                    {(categories[newExpense.category] || []).map(sub => (
                      <option key={sub} value={sub}>{sub}</option>
                    ))}
                  </Select>
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="description">Description (Optional)</Label>
                  <Input
                    id="description"
                    placeholder="What did you spend on?"
                    value={newExpense.description}
                    onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" size="lg">
                💾 Add Expense
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Calculator - 1/3 width */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>🔢 Calculator</CardTitle>
            <CardDescription>Quick calculations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {/* Display */}
              <div className="bg-theme-surface rounded-lg p-4 text-right">
                <div className="text-2xl font-bold text-number break-all">
                  {calcDisplay}
                </div>
              </div>

              {/* Buttons */}
              <div className="grid grid-cols-4 gap-2">
                {/* Row 1: AC and operations */}
                <button
                  type="button"
                  onClick={handleCalcClear}
                  className="col-span-2 bg-red-400 hover:bg-red-500 text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  AC
                </button>
                <button
                  type="button"
                  onClick={() => handleCalcOperation('/')}
                  className="bg-pastel-lavender hover:bg-pastel-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  ÷
                </button>
                <button
                  type="button"
                  onClick={() => handleCalcOperation('*')}
                  className="bg-pastel-lavender hover:bg-pastel-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  ×
                </button>

                {/* Row 2: 7 8 9 - */}
                {['7', '8', '9'].map(num => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => handleCalcNumber(num)}
                    className="bg-pastel-200 hover:bg-pastel-300 text-primary-foreground font-bold py-3 px-4 rounded-lg transition-colors"
                  >
                    {num}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => handleCalcOperation('-')}
                  className="bg-pastel-lavender hover:bg-pastel-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  −
                </button>

                {/* Row 3: 4 5 6 + */}
                {['4', '5', '6'].map(num => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => handleCalcNumber(num)}
                    className="bg-pastel-200 hover:bg-pastel-300 text-primary-foreground font-bold py-3 px-4 rounded-lg transition-colors"
                  >
                    {num}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => handleCalcOperation('+')}
                  className="bg-pastel-lavender hover:bg-pastel-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  +
                </button>

                {/* Row 4: 1 2 3 = */}
                {['1', '2', '3'].map(num => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => handleCalcNumber(num)}
                    className="bg-pastel-200 hover:bg-pastel-300 text-primary-foreground font-bold py-3 px-4 rounded-lg transition-colors"
                  >
                    {num}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={handleCalcEquals}
                  className="row-span-2 bg-primary hover:bg-pastel-rose text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  =
                </button>

                {/* Row 5: 0 . */}
                <button
                  type="button"
                  onClick={() => handleCalcNumber('0')}
                  className="col-span-2 bg-pastel-200 hover:bg-pastel-300 text-primary-foreground font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  0
                </button>
                <button
                  type="button"
                  onClick={handleCalcDecimal}
                  className="bg-pastel-200 hover:bg-pastel-300 text-primary-foreground font-bold py-3 px-4 rounded-lg transition-colors"
                >
                  .
                </button>
              </div>

              {/* Use Result Button */}
              <button
                type="button"
                onClick={handleUseCalcResult}
                className="w-full bg-gradient-to-r from-pastel-blue to-pastel-mint hover:opacity-90 text-white font-bold py-3 px-4 rounded-lg transition-opacity mt-2"
              >
                Use Result → Amount
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
      )}

      {/* Budget Tab */}
      {activeTab === 'budget' && fullBudgetComparison && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>💰 Budget Tracker</CardTitle>
              <CardDescription>Track your spending against your budget</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Total Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-theme-surface rounded-lg">
                  <div>
                    <p className="text-sm text-body">Total Budget</p>
                    <p className="text-2xl font-bold heading-section">
                      {formatCurrency(fullBudgetComparison.total_summary.total_budget)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-body">Total Spent</p>
                    <p className="text-2xl font-bold heading-section">
                      {formatCurrency(fullBudgetComparison.total_summary.total_spent)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-body">Remaining</p>
                    <p className={cn(
                      "text-2xl font-bold",
                      fullBudgetComparison.total_summary.total_remaining >= 0 ? "text-blue-600" : "text-red-600"
                    )}>
                      {formatCurrency(fullBudgetComparison.total_summary.total_remaining)}
                    </p>
                  </div>
                </div>

                {/* Category Breakdowns */}
                {Object.entries(fullBudgetComparison.comparison).map(([category, data]: [string, any]) => {
                  const percentage = data.percentage
                  const isOver = percentage > 100

                  return (
                    <div key={category} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <h3 className="font-semibold heading-section">{category}</h3>
                        <div className="text-right">
                          <p className="text-sm font-medium">
                            {formatCurrency(data.spent)} / {formatCurrency(data.budget)}
                          </p>
                          <p className={cn(
                            "text-xs font-semibold",
                            isOver ? "text-red-600" : percentage > 80 ? "text-yellow-600" : "text-blue-600"
                          )}>
                            {isOver ? `${(percentage - 100).toFixed(1)}% over` : `${formatCurrency(data.remaining)} left`}
                          </p>
                        </div>
                      </div>
                      <div className="w-full bg-theme-surface rounded-full h-4">
                        <div
                          className={cn(
                            "h-4 rounded-full transition-all",
                            isOver ? "bg-gradient-to-r from-red-400 to-red-600" :
                            percentage > 80 ? "bg-gradient-to-r from-yellow-400 to-yellow-600" :
                            "bg-gradient-to-r from-blue-400 to-blue-600"
                          )}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        />
                      </div>
                    </div>
                  )
                })}

                {/* Edit Budgets */}
                <div className="border-t border-theme-light pt-6 space-y-4">
                  <h3 className="font-semibold heading-section">Edit Monthly Budgets</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.keys(categories).map(category => (
                      <div key={category} className="space-y-2">
                        <Label>{category}</Label>
                        <Input
                          type="number"
                          step="0.01"
                          value={editingBudgets[category] || '0'}
                          onChange={(e) => setEditingBudgets({
                            ...editingBudgets,
                            [category]: e.target.value
                          })}
                        />
                      </div>
                    ))}
                  </div>
                  <Button onClick={handleSaveBudgets} className="w-full">
                    💾 Save Budgets
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recurring Tab */}
      {activeTab === 'recurring' && recurringStatus && (
        <div className="space-y-6">
          {/* Status Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Recurring</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-body">
                  {recurringStatus.total_recurring}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Applied This Month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {recurringStatus.applied}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Pending</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-600">
                  {recurringStatus.pending}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Monthly Total</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-body">
                  {formatCurrency(recurringStatus.total_amount)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Apply Pending */}
          {recurringStatus.pending > 0 && (
            <Card className="border-yellow-300 bg-yellow-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-yellow-800">
                      📌 You have {recurringStatus.pending} pending recurring transaction(s)
                    </p>
                    <p className="text-sm text-yellow-700 mt-1">
                      Click to automatically add them to your expenses
                    </p>
                  </div>
                  <Button onClick={handleApplyRecurring} variant="default" size="lg">
                    💚 Apply All Pending
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recurring List */}
          <Card>
            <CardHeader>
              <CardTitle>🔁 Your Recurring Transactions</CardTitle>
              <CardDescription>Manage monthly recurring expenses (locked expenses)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recurring.map(rec => {
                  const isActive = rec.is_active === 1
                  return (
                    <div key={rec.id} className={cn(
                      "flex items-center justify-between p-4 rounded-lg border",
                      isActive ? "border-theme-light bg-white" : "border-gray-200 bg-gray-50"
                    )}>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className={cn(
                            "text-2xl",
                            isActive ? "opacity-100" : "opacity-50"
                          )}>
                            {isActive ? '🟢' : '🔴'}
                          </span>
                          <div>
                            <p className="font-semibold heading-section">{rec.subcategory}</p>
                            <p className="text-sm text-body">{rec.category}</p>
                            <p className="text-xs text-muted-custom">{rec.description}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="text-xl font-bold text-body">{formatCurrency(rec.amount)}</p>
                          <p className="text-xs text-muted-custom">/month</p>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => handleToggleRecurring(rec.id, isActive)}
                            variant="outline"
                            size="sm"
                          >
                            {isActive ? 'Deactivate' : 'Activate'}
                          </Button>
                          <Button
                            onClick={() => handleDeleteRecurring(rec.id)}
                            variant="destructive"
                            size="sm"
                          >
                            🗑️
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Add New Recurring */}
          <Card>
            <CardHeader>
              <CardTitle>➕ Add New Recurring Transaction</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddRecurring} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Category</Label>
                    <Select
                      value={newRecurring.category}
                      onChange={(e) => setNewRecurring({
                        ...newRecurring,
                        category: e.target.value,
                        subcategory: categories[e.target.value]?.[0] || ''
                      })}
                      required
                    >
                      {Object.keys(categories).map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Subcategory</Label>
                    <Select
                      value={newRecurring.subcategory}
                      onChange={(e) => setNewRecurring({ ...newRecurring, subcategory: e.target.value })}
                      required
                    >
                      {(categories[newRecurring.category] || []).map(sub => (
                        <option key={sub} value={sub}>{sub}</option>
                      ))}
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Monthly Amount (RM)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={newRecurring.amount}
                      onChange={(e) => setNewRecurring({ ...newRecurring, amount: e.target.value })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Input
                      placeholder="e.g., Monthly rent"
                      value={newRecurring.description}
                      onChange={(e) => setNewRecurring({ ...newRecurring, description: e.target.value })}
                    />
                  </div>
                </div>

                <Button type="submit" className="w-full">
                  ➕ Add Recurring Transaction
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (() => {
        // Calculate pagination
        const totalPages = Math.ceil(expenses.length / rowsPerPage)
        const startIndex = (currentPage - 1) * rowsPerPage
        const endIndex = startIndex + rowsPerPage
        const paginatedExpenses = expenses.slice(startIndex, endIndex)

        return (
          <Card>
            <CardHeader>
              <CardTitle>📝 Transaction History</CardTitle>
              <CardDescription>
                All your recorded expenses ({expenses.length} total)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {expenses.length === 0 ? (
                <div className="text-center py-12 text-muted-custom">
                  <p className="text-lg">No expenses recorded yet.</p>
                  <p className="text-sm mt-2">Start by adding your first expense! 🌊</p>
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-theme-light">
                          <th className="text-left py-3 px-4 heading-section">Date</th>
                          <th className="text-left py-3 px-4 heading-section">Category</th>
                          <th className="text-left py-3 px-4 heading-section">Subcategory</th>
                          <th className="text-left py-3 px-4 heading-section">Description</th>
                          <th className="text-right py-3 px-4 heading-section">Amount</th>
                          <th className="text-center py-3 px-4 heading-section">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedExpenses.map(expense => (
                      <tr key={expense.id} className={cn(
                        "border-b border-theme-light hover:bg-theme-surface",
                        expense.is_recurring ? "bg-blue-50/50" : ""
                      )}>
                        <td className="py-3 px-4 text-sm text-body">{formatDate(expense.date)}</td>
                        <td className="py-3 px-4 text-sm text-body">
                          <div className="flex items-center gap-2">
                            {expense.category}
                            {expense.is_recurring === 1 && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                                🔒 Locked
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm font-medium heading-section">{expense.subcategory}</td>
                        <td className="py-3 px-4 text-sm text-muted-custom">{expense.description || '-'}</td>
                        <td className="py-3 px-4 text-sm font-bold text-body text-right">
                          {formatCurrency(expense.amount)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex space-x-2 justify-center">
                            <Button
                              onClick={() => handleEditExpense(expense)}
                              variant="outline"
                              size="sm"
                            >
                              ✏️
                            </Button>
                            <Button
                              onClick={() => handleDeleteExpense(expense.id)}
                              variant="destructive"
                              size="sm"
                            >
                              🗑️
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination Controls */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-between mt-6 pt-4 border-t border-theme-light">
                      <div className="text-sm text-muted-custom">
                        Showing {startIndex + 1} to {Math.min(endIndex, expenses.length)} of {expenses.length} expenses
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={currentPage === 1}
                          variant="outline"
                          size="sm"
                        >
                          ← Previous
                        </Button>
                        <div className="flex items-center px-4 text-sm font-medium">
                          Page {currentPage} of {totalPages}
                        </div>
                        <Button
                          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                          disabled={currentPage === totalPages}
                          variant="outline"
                          size="sm"
                        >
                          Next →
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        )
      })()}

      {/* Edit Expense Modal */}
      {editingExpense && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl">
            <CardHeader>
              <CardTitle>✏️ Edit Expense</CardTitle>
              <CardDescription>Update expense details</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateExpense} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="edit-date">Date</Label>
                    <Input
                      id="edit-date"
                      type="date"
                      value={toDateInputValue(editingExpense.date)}
                      onChange={(e) => setEditingExpense({ ...editingExpense, date: e.target.value })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-amount">Amount (RM)</Label>
                    <Input
                      id="edit-amount"
                      type="number"
                      step="0.01"
                      value={editingExpense.amount}
                      onChange={(e) => setEditingExpense({ ...editingExpense, amount: parseFloat(e.target.value) })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-category">Category</Label>
                    <Select
                      id="edit-category"
                      value={editingExpense.category}
                      onChange={(e) => setEditingExpense({
                        ...editingExpense,
                        category: e.target.value,
                        subcategory: categories[e.target.value]?.[0] || ''
                      })}
                      required
                    >
                      {Object.keys(categories).map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-subcategory">Subcategory</Label>
                    <Select
                      id="edit-subcategory"
                      value={editingExpense.subcategory}
                      onChange={(e) => setEditingExpense({ ...editingExpense, subcategory: e.target.value })}
                      required
                    >
                      {(categories[editingExpense.category] || []).map(sub => (
                        <option key={sub} value={sub}>{sub}</option>
                      ))}
                    </Select>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="edit-description">Description (Optional)</Label>
                    <Input
                      id="edit-description"
                      placeholder="What did you spend on?"
                      value={editingExpense.description}
                      onChange={(e) => setEditingExpense({ ...editingExpense, description: e.target.value })}
                    />
                  </div>
                </div>

                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1" size="lg">
                    💾 Update Expense
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                    size="lg"
                    onClick={() => setEditingExpense(null)}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
