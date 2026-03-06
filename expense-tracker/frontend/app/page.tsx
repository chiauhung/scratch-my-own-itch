'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function HomePage() {
  const modules = [
    {
      title: '💰 Expense Tracker',
      description: 'Track your spending and manage your budget',
      href: '/expense-tracker',
      status: 'Active',
      color: 'from-blue-50 to-cyan-50 border-blue-200'
    },
    {
      title: '🍽️ Meal Planner',
      description: 'Plan your meals and manage recipes',
      href: '/meal-planner',
      status: 'Coming Soon',
      color: 'from-green-50 to-emerald-50 border-green-200'
    },
    {
      title: '📈 Savings & Investment',
      description: 'Monitor your savings and investment portfolio',
      href: '/savings',
      status: 'Coming Soon',
      color: 'from-purple-50 to-violet-50 border-purple-200'
    },
    {
      title: '📓 Journal',
      description: 'Reflect and document your daily thoughts',
      href: '/journal',
      status: 'Coming Soon',
      color: 'from-amber-50 to-yellow-50 border-amber-200'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            🌊 Life Dashboard
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Your all-in-one platform for managing finances, habits, savings, and reflections
          </p>
        </div>

        {/* Module Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
          {modules.map((module) => (
            <Link key={module.href} href={module.href}>
              <Card className={`h-full transition-all duration-300 hover:shadow-xl hover:scale-105 cursor-pointer bg-gradient-to-br ${module.color} border-2`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-2xl mb-2">{module.title}</CardTitle>
                      <CardDescription className="text-base">{module.description}</CardDescription>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      module.status === 'Active'
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-600 border border-gray-300'
                    }`}>
                      {module.status}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center text-sm font-medium text-gray-700">
                    {module.status === 'Active' ? (
                      <>
                        <span className="mr-2">Open Module</span>
                        <span>→</span>
                      </>
                    ) : (
                      <span className="text-gray-500">Under Development</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Footer Info */}
        <div className="text-center mt-12 text-sm text-gray-500">
          <p>Build your best life, one module at a time.</p>
        </div>
      </div>
    </div>
  )
}
