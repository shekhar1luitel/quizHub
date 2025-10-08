"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { BarChart3, TrendingUp, TrendingDown, Target, Clock, BookOpen, Trophy, ArrowLeft } from "lucide-react"
import Link from "next/link"

// Mock analytics data
const mockAnalytics = {
  overallStats: {
    totalTests: 25,
    averageScore: 78,
    totalTimeSpent: 15600, // seconds
    improvementRate: 12, // percentage
    streak: 7, // days
  },
  categoryPerformance: [
    { category: "General Knowledge", tests: 8, averageScore: 82, bestScore: 95, improvement: 15 },
    { category: "Aptitude", tests: 6, averageScore: 75, bestScore: 88, improvement: 8 },
    { category: "Reasoning", tests: 5, averageScore: 85, bestScore: 92, improvement: 18 },
    { category: "English", tests: 3, averageScore: 68, bestScore: 78, improvement: -5 },
    { category: "Mathematics", tests: 3, averageScore: 72, bestScore: 85, improvement: 22 },
  ],
  weeklyProgress: [
    { week: "Week 1", tests: 3, averageScore: 65 },
    { week: "Week 2", tests: 5, averageScore: 72 },
    { week: "Week 3", tests: 4, averageScore: 78 },
    { week: "Week 4", tests: 6, averageScore: 82 },
    { week: "Week 5", tests: 7, averageScore: 85 },
  ],
  timeAnalysis: {
    averageTimePerQuestion: 45, // seconds
    fastestTest: 1200, // seconds
    slowestTest: 2400, // seconds
    optimalTimeRange: [30, 60], // seconds per question
  },
  strengths: ["Pattern Recognition", "Logical Reasoning", "World Geography"],
  weaknesses: ["Grammar Rules", "Mathematical Calculations", "Current Events"],
}

export default function AnalyticsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState("month")

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getImprovementColor = (improvement: number) => {
    if (improvement > 0) return "text-green-600"
    if (improvement < 0) return "text-red-600"
    return "text-muted-foreground"
  }

  const getImprovementIcon = (improvement: number) => {
    if (improvement > 0) return <TrendingUp className="h-4 w-4" />
    if (improvement < 0) return <TrendingDown className="h-4 w-4" />
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-8 w-8 text-secondary" />
                <h1 className="text-2xl font-bold text-foreground">Performance Analytics</h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
                <option value="year">This Year</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockAnalytics.overallStats.totalTests}</div>
              <p className="text-xs text-muted-foreground">completed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getScoreColor(mockAnalytics.overallStats.averageScore)}`}>
                {mockAnalytics.overallStats.averageScore}%
              </div>
              <Progress value={mockAnalytics.overallStats.averageScore} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Study Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatTime(mockAnalytics.overallStats.totalTimeSpent)}</div>
              <p className="text-xs text-muted-foreground">total time</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Improvement</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">+{mockAnalytics.overallStats.improvementRate}%</div>
              <p className="text-xs text-muted-foreground">vs last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Study Streak</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-secondary">{mockAnalytics.overallStats.streak}</div>
              <p className="text-xs text-muted-foreground">days</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Category Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Category Performance</CardTitle>
              <CardDescription>Your performance across different subjects</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAnalytics.categoryPerformance.map((category) => (
                  <div key={category.category} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{category.category}</span>
                        <Badge variant="outline" className="text-xs">
                          {category.tests} tests
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-bold ${getScoreColor(category.averageScore)}`}>
                          {category.averageScore}%
                        </span>
                        <div className={`flex items-center gap-1 ${getImprovementColor(category.improvement)}`}>
                          {getImprovementIcon(category.improvement)}
                          <span className="text-xs">{Math.abs(category.improvement)}%</span>
                        </div>
                      </div>
                    </div>
                    <Progress value={category.averageScore} className="h-2" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Avg: {category.averageScore}%</span>
                      <span>Best: {category.bestScore}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Weekly Progress */}
          <Card>
            <CardHeader>
              <CardTitle>Weekly Progress</CardTitle>
              <CardDescription>Your improvement over the past 5 weeks</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAnalytics.weeklyProgress.map((week, index) => (
                  <div key={week.week} className="flex items-center gap-4">
                    <div className="w-16 text-sm text-muted-foreground">{week.week}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm">{week.tests} tests</span>
                        <span className={`text-sm font-bold ${getScoreColor(week.averageScore)}`}>
                          {week.averageScore}%
                        </span>
                      </div>
                      <Progress value={week.averageScore} className="h-2" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Time Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Time Analysis</CardTitle>
              <CardDescription>Your test-taking speed insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Avg per question</span>
                  <span className="font-medium">{mockAnalytics.timeAnalysis.averageTimePerQuestion}s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Fastest test</span>
                  <span className="font-medium">{formatTime(mockAnalytics.timeAnalysis.fastestTest)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Slowest test</span>
                  <span className="font-medium">{formatTime(mockAnalytics.timeAnalysis.slowestTest)}</span>
                </div>
                <div className="pt-2 border-t border-border">
                  <p className="text-xs text-muted-foreground mb-2">Optimal time per question:</p>
                  <p className="text-sm font-medium text-secondary">
                    {mockAnalytics.timeAnalysis.optimalTimeRange[0]}s - {mockAnalytics.timeAnalysis.optimalTimeRange[1]}
                    s
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Strengths */}
          <Card>
            <CardHeader>
              <CardTitle>Your Strengths</CardTitle>
              <CardDescription>Topics you excel at</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockAnalytics.strengths.map((strength, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-sm">{strength}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Areas for Improvement */}
          <Card>
            <CardHeader>
              <CardTitle>Areas for Improvement</CardTitle>
              <CardDescription>Topics to focus on</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockAnalytics.weaknesses.map((weakness, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                    <span className="text-sm">{weakness}</span>
                  </div>
                ))}
              </div>
              <div className="pt-4 border-t border-border mt-4">
                <Button size="sm" className="w-full" asChild>
                  <Link href="/categories">Practice These Topics</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
