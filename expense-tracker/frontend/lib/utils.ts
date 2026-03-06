import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return `RM ${amount.toFixed(2)}`
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-MY', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

export function toDateInputValue(date: string): string {
  // Convert any date string to YYYY-MM-DD format for HTML date inputs
  const dateObj = new Date(date)
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function getCurrentMonth(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

export function getMonthDates(monthStr: string): { start: string; end: string } {
  const [year, month] = monthStr.split('-').map(Number)

  // Build date strings directly to avoid timezone issues
  const startDay = '01'

  // Calculate last day of month
  const lastDay = new Date(year, month, 0).getDate()
  const endDay = String(lastDay).padStart(2, '0')

  return {
    start: `${year}-${String(month).padStart(2, '0')}-${startDay}`,
    end: `${year}-${String(month).padStart(2, '0')}-${endDay}`
  }
}
