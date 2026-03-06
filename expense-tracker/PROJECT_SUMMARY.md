# Life Dashboard - Project Summary

**Version:** 2.0.0
**Last Updated:** 2025-10-31

---

## Overview

Life Dashboard is an integrated web application for managing personal life aspects including expenses, habits, savings/investments, and journaling. Built with modern web technologies (Next.js, FastAPI, SQLite), it provides a clean, modular architecture for future expansion.

**Current Status:**
- ✅ **Expense Tracker**: Fully functional
- ✅ **Meal Planner**: Fully functional
- 🚧 **Savings & Investment**: Planned
- 🚧 **Journal**: Planned

---

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components based on shadcn/ui
- **State Management**: React hooks (useState, useEffect)

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite
- **Architecture**: Clean architecture with service layers
- **ORM**: Pandas (for data manipulation)

---

## Project Structure

### Frontend Structure

```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Main landing page with module navigation
│   ├── expense-tracker/
│   │   └── page.tsx                  # Expense tracker (fully functional)
│   ├── meal-planner/
│   │   └── page.tsx                  # Meal planner (fully functional)
│   ├── savings/
│   │   └── page.tsx                  # Placeholder
│   └── journal/
│       └── page.tsx                  # Placeholder
├── components/
│   └── ui/                           # Reusable UI components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── select.tsx
│       └── tabs.tsx
├── lib/
│   ├── api.ts                        # API client for backend communication
│   └── utils.ts                      # Utility functions
└── globals.css                       # Global styles
```

### Backend Structure

```
backend/
├── api.py                            # Main FastAPI application with all routes
├── config.py                         # Configuration (categories, budgets)
├── database/
│   ├── sqlite_impl.py                # SQLite database implementation
│   └── __init__.py
├── services/
│   ├── expense_service.py            # Expense business logic (ACTIVE)
│   ├── budget_service.py             # Budget business logic (ACTIVE)
│   ├── recurring_service.py          # Recurring transactions logic (ACTIVE)
│   ├── meal_service.py               # Meal planning business logic (ACTIVE)
│   ├── savings_service.py            # Placeholder for savings/investment
│   └── journal_service.py            # Placeholder for journaling
├── data/
│   └── expenses.db                   # SQLite database file
└── requirements.txt                  # Python dependencies
```

---

## Module Details

### 1. Expense Tracker (ACTIVE)

#### Features
- ✅ Add, edit, delete expenses
- ✅ Monthly filtering with global month selector
- ✅ Budget tracking and comparison
- ✅ Recurring transactions management
- ✅ Category and subcategory organization
- ✅ Dashboard with charts and statistics
- ✅ Transaction history with pagination (50 rows/page)
- ✅ Built-in calculator for quick calculations
- ✅ Export-ready data structure

#### Key Components

**Frontend:**
- `/expense-tracker/page.tsx` - Main expense tracker page (1300+ lines)
  - Dashboard tab: Monthly overview, charts, budget vs actual
  - Add Expense tab: Form with calculator (2:1 ratio)
  - Budgets tab: Monthly budget management
  - Recurring tab: Manage recurring transactions
  - History tab: Paginated transaction history

**Backend:**
- `services/expense_service.py` - Expense CRUD, summaries, analytics
- `services/budget_service.py` - Budget management and comparison
- `services/recurring_service.py` - Recurring transaction automation
- `database/sqlite_impl.py` - Database operations

**Database Tables:**
- `expenses` - All expense records
- `budgets` - Monthly budget allocations
- `recurring_transactions` - Template for recurring expenses
- `applied_recurring` - Tracking of applied recurring expenses

#### API Endpoints

**Configuration:**
- `GET /config/categories` - Get expense categories
- `GET /config/default-budgets` - Get default budgets

**Expenses:**
- `GET /expenses` - Get all expenses (with optional date filter)
- `POST /expenses` - Add new expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `GET /expenses/summary` - Get expense statistics
- `GET /expenses/by-category` - Spending by category
- `GET /expenses/daily` - Daily spending trends
- `GET /expenses/available-months` - Get available month list

**Budgets:**
- `GET /budgets/{month}` - Get budgets for month
- `PUT /budgets/{month}` - Update budgets
- `GET /budgets/{month}/comparison` - Budget vs actual comparison

**Recurring:**
- `GET /recurring` - Get all recurring transactions
- `POST /recurring` - Add recurring transaction
- `PUT /recurring/{id}` - Update recurring transaction
- `DELETE /recurring/{id}` - Delete recurring transaction
- `GET /recurring/status/{month}` - Check status for month
- `POST /recurring/apply/{month}` - Apply recurring for month

---

### 2. Meal Planner (ACTIVE)

#### Features
- ✅ Recipe management with categories
- ✅ Weekly meal planning calendar
- ✅ Meal types: breakfast, lunch, dinner, snack
- ✅ Recipe details: ingredients, instructions, servings, prep time
- ✅ Automatic grocery list generation
- ✅ Ingredient aggregation from multiple recipes
- ✅ Weekly navigation (previous/next/current week)
- ✅ Full CRUD operations for recipes and meal plans

#### Key Components

**Frontend:**
- `/meal-planner/page.tsx` - Main meal planner page with tabs
  - Weekly Planner tab: Calendar grid for meal scheduling
  - Recipes tab: Recipe library management
  - Grocery List tab: Auto-generated shopping list

**Backend:**
- `services/meal_service.py` - Meal planning and recipe logic
  - Recipe CRUD operations
  - Meal plan CRUD operations
  - Grocery list generation with ingredient aggregation
  - Meal planning statistics

**Database Tables:**
- `recipes` - Recipe database with ingredients and instructions
- `meal_plans` - Scheduled meals with dates and meal types

#### API Endpoints

**Recipes:**
- `GET /recipes` - Get all recipes (with optional category filter)
- `GET /recipes/{id}` - Get single recipe
- `POST /recipes` - Add new recipe
- `PUT /recipes/{id}` - Update recipe
- `DELETE /recipes/{id}` - Delete recipe

**Meal Plans:**
- `GET /meal-plans` - Get meal plans (with optional date filter)
- `GET /meal-plans/{id}` - Get single meal plan
- `POST /meal-plans` - Add meal to plan
- `PUT /meal-plans/{id}` - Update meal plan
- `DELETE /meal-plans/{id}` - Delete meal plan

**Grocery List:**
- `GET /grocery-list?start_date=X&end_date=Y` - Generate grocery list for date range

**Statistics:**
- `GET /meal-plans/stats` - Get meal planning statistics

#### Database Schema

```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT,
    servings INTEGER DEFAULT 4,
    prep_time INTEGER DEFAULT 30,
    nutrition_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE meal_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    recipe_id INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);
```

---

### 3. Savings & Investment (PLANNED)

#### Planned Features
- Track savings accounts and balances
- Investment portfolio tracking (stocks, crypto, funds)
- Net worth calculation and trends
- Savings goals and progress tracking
- Asset allocation visualization
- ROI and performance analytics

#### Placeholder Files Created
- Frontend: `/app/savings/page.tsx`
- Backend: `/backend/services/savings_service.py`

#### Planned API Endpoints
```
GET  /savings/accounts - Get all savings accounts
POST /savings/accounts - Create a savings account
GET  /investments - Get all investments
POST /investments - Add an investment
GET  /net-worth - Calculate total net worth
GET  /portfolio/allocation - Get asset allocation
```

#### Planned Database Tables
```sql
CREATE TABLE savings_accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    account_type TEXT, -- savings, checking, etc
    current_balance REAL,
    currency TEXT DEFAULT 'MYR',
    created_at TIMESTAMP
);

CREATE TABLE investments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    investment_type TEXT, -- stock, crypto, fund, etc
    quantity REAL,
    purchase_price REAL,
    current_price REAL,
    currency TEXT DEFAULT 'MYR',
    purchase_date TEXT,
    created_at TIMESTAMP
);

CREATE TABLE balance_history (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    date TEXT NOT NULL,
    balance REAL,
    FOREIGN KEY (account_id) REFERENCES savings_accounts(id)
);
```

---

### 4. Journal (PLANNED)

#### Planned Features
- Daily journal entries with rich text editor
- Mood tracking and emotional insights
- Tags and categories for entries
- Search and filter past entries
- Gratitude log and reflections
- Calendar view of journal history

#### Placeholder Files Created
- Frontend: `/app/journal/page.tsx`
- Backend: `/backend/services/journal_service.py`

#### Planned API Endpoints
```
GET    /journal/entries - Get all journal entries
POST   /journal/entries - Create a journal entry
PUT    /journal/entries/{entry_id} - Update an entry
DELETE /journal/entries/{entry_id} - Delete an entry
GET    /journal/search - Search journal entries
GET    /journal/moods - Get mood statistics
```

#### Planned Database Tables
```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    mood TEXT, -- happy, sad, neutral, etc
    created_at TIMESTAMP
);

CREATE TABLE journal_tags (
    id INTEGER PRIMARY KEY,
    entry_id INTEGER,
    tag TEXT,
    FOREIGN KEY (entry_id) REFERENCES journal_entries(id)
);

CREATE TABLE gratitude_log (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    gratitude_text TEXT NOT NULL,
    created_at TIMESTAMP
);
```

---

## Key Design Patterns

### 1. Clean Architecture
- **Presentation Layer**: React components
- **API Layer**: FastAPI endpoints
- **Business Logic**: Service classes
- **Data Access**: Database implementation

### 2. Separation of Concerns
- Each module has its own service file
- Database operations isolated in `sqlite_impl.py`
- API routes organized by module
- Frontend pages separated by feature

### 3. Modular Structure
- Easy to add new modules
- Shared components in `/components/ui`
- Shared utilities in `/lib`
- Each module can be developed independently

---

## Data Flow

### Frontend → Backend
```
User Action (UI Component)
    ↓
API Call (lib/api.ts)
    ↓
HTTP Request
    ↓
FastAPI Endpoint (api.py)
    ↓
Service Layer (services/*.py)
    ↓
Database (database/sqlite_impl.py)
    ↓
SQLite (data/expenses.db)
```

### Backend → Frontend
```
SQLite Query Result
    ↓
Pandas DataFrame
    ↓
Service Processing
    ↓
JSON Response
    ↓
Frontend State Update
    ↓
UI Re-render
```

---

## Development Workflow

### Starting the Application

**Backend:**
```bash
cd backend
.venv/bin/python api.py
# Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Adding a New Module

1. **Create Frontend Page**
   ```bash
   mkdir -p frontend/app/new-module
   touch frontend/app/new-module/page.tsx
   ```

2. **Create Backend Service**
   ```bash
   touch backend/services/new_module_service.py
   ```

3. **Add Database Tables**
   - Update `database/sqlite_impl.py` with new table initialization
   - Create migration script if needed

4. **Add API Endpoints**
   - Add routes in `api.py`
   - Import and initialize service

5. **Update Navigation**
   - Add module card to main `page.tsx`

---

## Configuration

### Expense Categories (config.py)
```python
CATEGORIES = {
    "固定支出 (Fixed Expenses)": [...],
    "生活必要支出 (Essential Living)": [...],
    "生活质量支出 (Quality of Life)": [...],
    "基金 (Fund/Savings)": [...]
}
```

### CORS Configuration (api.py)
```python
allow_origins=["http://localhost:3000"]
```

---

## Future Enhancements

### Authentication & Deployment
- [ ] Add user authentication (Google OAuth via NextAuth.js)
- [ ] Migrate from SQLite to PostgreSQL for multi-user support
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway or Render
- [ ] Add environment variable management

### Mobile Support
- [ ] PWA (Progressive Web App) configuration
- [ ] Responsive design optimization
- [ ] Touch-friendly UI improvements

### Data Features
- [ ] Export data to CSV/Excel
- [ ] Import data from spreadsheets
- [ ] Data backup and restore
- [ ] Multi-currency support

### Analytics
- [ ] Advanced charting (Chart.js or Recharts)
- [ ] Trend analysis
- [ ] Predictive budgeting
- [ ] Custom report generation

---

## Known Issues & Limitations

1. **Frontend Refresh Required**: After adding expenses, manual refresh needed to see updates
   - **Status**: Known issue
   - **Workaround**: Use Cmd+R/Ctrl+R after adding expense
   - **Fix**: Auto-refresh already implemented via `refreshKey`, may be timing issue

2. **Single User**: Currently designed for single user (no authentication)
   - **Status**: By design for current version
   - **Fix**: Requires authentication implementation

3. **SQLite Limitations**: File-based database, not suitable for concurrent users
   - **Status**: Acceptable for personal use
   - **Fix**: Migrate to PostgreSQL when adding multi-user support

---

## File Locations Reference

### Important Files

**Frontend:**
- Main page: `frontend/app/page.tsx`
- Expense tracker: `frontend/app/expense-tracker/page.tsx`
- Meal planner: `frontend/app/meal-planner/page.tsx`
- API client: `frontend/lib/api.ts`
- Utilities: `frontend/lib/utils.ts`
- Styles: `frontend/app/globals.css`

**Backend:**
- Main API: `backend/api.py`
- Config: `backend/config.py`
- Database: `backend/database/sqlite_impl.py`
- Expense service: `backend/services/expense_service.py`
- Budget service: `backend/services/budget_service.py`
- Recurring service: `backend/services/recurring_service.py`
- Meal service: `backend/services/meal_service.py`

**Database:**
- SQLite file: `backend/data/expenses.db`

**Documentation:**
- This file: `PROJECT_SUMMARY.md`

---

## Development Timeline

### Phase 1: Expense Tracker (COMPLETED)
- ✅ Basic CRUD operations
- ✅ Monthly filtering
- ✅ Budget management
- ✅ Recurring transactions
- ✅ Dashboard and analytics
- ✅ Pagination
- ✅ Calculator integration

### Phase 2: Project Restructuring (COMPLETED)
- ✅ Multi-module architecture
- ✅ Landing page with navigation
- ✅ Placeholder pages
- ✅ Backend service organization
- ✅ Documentation

### Phase 3: Meal Planner (COMPLETED)
- ✅ Design database schema
- ✅ Implement service layer
- ✅ Create API endpoints
- ✅ Build frontend UI
- ✅ Add recipe management
- ✅ Implement weekly calendar view
- ✅ Create grocery list generation

### Phase 4: Savings & Investment (PLANNED)
- [ ] Design database schema
- [ ] Implement service layer
- [ ] Create API endpoints
- [ ] Build frontend UI
- [ ] Add portfolio tracking
- [ ] Implement ROI calculations

### Phase 5: Journal (PLANNED)
- [ ] Design database schema
- [ ] Implement service layer
- [ ] Create API endpoints
- [ ] Build frontend UI with rich text editor
- [ ] Add mood tracking
- [ ] Implement search functionality

### Phase 6: Authentication & Deployment (PLANNED)
- [ ] Implement Google OAuth
- [ ] Migrate to PostgreSQL
- [ ] Deploy to production
- [ ] Setup CI/CD pipeline

---

## Notes

- All monetary values stored in database default currency (assumed MYR)
- Dates stored in ISO format (YYYY-MM-DD)
- Month format: YYYY-MM (e.g., "2025-10")
- Frontend display format: "October 25" (Month YY)
- All services return Pandas DataFrames or dictionaries
- API returns JSON responses
- Frontend uses TypeScript for type safety

---

## Quick Reference Commands

```bash
# Backend
cd backend
.venv/bin/python api.py

# Frontend
cd frontend
npm run dev

# Database query
sqlite3 backend/data/expenses.db "SELECT * FROM expenses LIMIT 10;"

# Kill port 8000
lsof -ti:8000 | xargs kill -9

# Install frontend dependencies
cd frontend && npm install

# Install backend dependencies
cd backend && pip install -r requirements.txt
```

---

## Contact & Maintenance

This is a personal project for managing life aspects.
For questions or issues, refer to this documentation or check the codebase comments.

**Last Major Update:** 2024-12-24 - Added Meal Planner module with full recipe management and grocery list features
