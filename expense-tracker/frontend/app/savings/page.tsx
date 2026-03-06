'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function SavingsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50 p-8">
      <div className="container mx-auto max-w-4xl">
        {/* Back Button */}
        <Link href="/">
          <Button variant="outline" className="mb-6">
            ← Back to Dashboard
          </Button>
        </Link>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent mb-4">
            📈 Savings & Investment
          </h1>
          <p className="text-lg text-gray-600">
            Monitor your savings and investment portfolio
          </p>
        </div>

        {/* Placeholder Card */}
        <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-white">
          <CardHeader>
            <CardTitle className="text-2xl">Coming Soon!</CardTitle>
            <CardDescription className="text-base">
              This module is under development
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg mb-3 text-purple-700">Planned Features:</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Track savings accounts and balances</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Investment portfolio tracking (stocks, crypto, funds)</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Net worth calculation and trends</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Savings goals and progress tracking</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Asset allocation visualization</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>ROI and performance analytics</span>
                </li>
              </ul>
            </div>

            <div className="pt-4 border-t border-purple-200">
              <p className="text-sm text-gray-500 italic">
                This page will be implemented in the future. Stay tuned!
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
