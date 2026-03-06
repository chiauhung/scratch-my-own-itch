'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function JournalPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-yellow-50 p-8">
      <div className="container mx-auto max-w-4xl">
        {/* Back Button */}
        <Link href="/">
          <Button variant="outline" className="mb-6">
            ← Back to Dashboard
          </Button>
        </Link>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-amber-600 to-yellow-600 bg-clip-text text-transparent mb-4">
            📓 Journal
          </h1>
          <p className="text-lg text-gray-600">
            Reflect and document your daily thoughts
          </p>
        </div>

        {/* Placeholder Card */}
        <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-white">
          <CardHeader>
            <CardTitle className="text-2xl">Coming Soon!</CardTitle>
            <CardDescription className="text-base">
              This module is under development
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg mb-3 text-amber-700">Planned Features:</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Daily journal entries with rich text editor</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Mood tracking and emotional insights</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Tags and categories for entries</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Search and filter past entries</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Gratitude log and reflections</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>Calendar view of journal history</span>
                </li>
              </ul>
            </div>

            <div className="pt-4 border-t border-amber-200">
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
