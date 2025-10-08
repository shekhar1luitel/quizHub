"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Users,
  BookOpen,
  Trophy,
  BarChart3,
  Settings,
  Plus,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react"
import Link from "next/link"

// Mock admin data
const mockAdminStats = {
  totalUsers: 1247,
  activeUsers: 892,
  totalQuestions: 2450,
  totalCategories: 12,
  testsToday: 156,
  averageScore: 76,
  systemHealth: 98,
  pendingReports: 3,
}

const mockRecentActivity = [
  { id: 1, user: "John Doe", action: "Completed GK Quiz", score: 85, time: "2 minutes ago" },
  { id: 2, user: "Jane Smith", action: "Started Aptitude Test", score: null, time: "5 minutes ago" },
  { id: 3, user: "Mike Johnson", action: "Completed Math Quiz", score: 92, time: "8 minutes ago" },
  { id: 4, user: "Sarah Wilson", action: "Registered", score: null, time: "12 minutes ago" },
  { id: 5, user: "Tom Brown", action: "Completed Reasoning Test", score: 78, time: "15 minutes ago" },
]

const mockCategoryStats = [
  { name: "General Knowledge", questions: 500, tests: 1250, avgScore: 78 },
  { name: "Aptitude", questions: 300, tests: 890, avgScore: 72 },
  { name: "Reasoning", questions: 400, tests: 1100, avgScore: 81 },
  { name: "English", questions: 250, tests: 650, avgScore: 69 },
  { name: "Mathematics", questions: 350, tests: 780, avgScore: 74 },
  { name: "Current Affairs", questions: 200, tests: 420, avgScore: 76 },
]

export default function AdminDashboard() {
  const [selectedPeriod, setSelectedPeriod] = useState("today")

  return (
    <div className="min-h-screen bg-background">
      {/* Admin Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Settings className="h-8 w-8 text-secondary" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">Admin Dashboard</h1>
                <p className="text-sm text-muted-foreground">QuizMaster Management Panel</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
              <Button asChild>
                <Link href="/admin/questions/new">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Question
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Admin Navigation */}
      <nav className="border-b border-border bg-card/50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center gap-6">
            <Link
              href="/admin"
              className="flex items-center gap-2 px-3 py-2 rounded-md bg-secondary text-secondary-foreground text-sm font-medium"
            >
              <BarChart3 className="h-4 w-4" />
              Dashboard
            </Link>
            <Link
              href="/admin/questions"
              className="flex items-center gap-2 px-3 py-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent text-sm font-medium"
            >
              <BookOpen className="h-4 w-4" />
              Questions
            </Link>
            <Link
              href="/admin/categories"
              className="flex items-center gap-2 px-3 py-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent text-sm font-medium"
            >
              <Settings className="h-4 w-4" />
              Categories
            </Link>
            <Link
              href="/admin/users"
              className="flex items-center gap-2 px-3 py-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent text-sm font-medium"
            >
              <Users className="h-4 w-4" />
              Users
            </Link>
            <Link
              href="/admin/reports"
              className="flex items-center gap-2 px-3 py-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent text-sm font-medium"
            >
              <Trophy className="h-4 w-4" />
              Reports
            </Link>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* System Health Alert */}
        {mockAdminStats.pendingReports > 0 && (
          <Card className="mb-6 border-yellow-200 bg-yellow-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="font-medium text-yellow-800">
                    {mockAdminStats.pendingReports} pending reports require attention
                  </p>
                  <p className="text-sm text-yellow-700">Review user reports and system issues</p>
                </div>
                <Button size="sm" variant="outline" className="ml-auto bg-transparent" asChild>
                  <Link href="/admin/reports">Review Reports</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockAdminStats.totalUsers.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">{mockAdminStats.activeUsers}</span> active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Questions Bank</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockAdminStats.totalQuestions.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">{mockAdminStats.totalCategories} categories</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tests Today</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockAdminStats.testsToday}</div>
              <div className="flex items-center gap-1 text-xs text-green-600">
                <TrendingUp className="h-3 w-3" />
                +12% vs yesterday
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{mockAdminStats.systemHealth}%</div>
              <Progress value={mockAdminStats.systemHealth} className="mt-2" />
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Category Performance */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Category Performance</CardTitle>
                <CardDescription>Question bank and test statistics by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockCategoryStats.map((category) => (
                    <div key={category.name} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{category.name}</span>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{category.questions} questions</span>
                          <span>{category.tests} tests</span>
                          <Badge variant="outline">{category.avgScore}% avg</Badge>
                        </div>
                      </div>
                      <Progress value={category.avgScore} className="h-2" />
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <Button variant="outline" className="w-full bg-transparent" asChild>
                    <Link href="/admin/categories">Manage Categories</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest user actions and system events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockRecentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full bg-secondary mt-2"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">{activity.user}</p>
                        <p className="text-xs text-muted-foreground">{activity.action}</p>
                        {activity.score && (
                          <Badge variant="outline" className="text-xs mt-1">
                            {activity.score}%
                          </Badge>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <Button variant="outline" className="w-full bg-transparent" asChild>
                    <Link href="/admin/users">View All Users</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button className="w-full justify-start" asChild>
                    <Link href="/admin/questions/new">
                      <Plus className="h-4 w-4 mr-2" />
                      Add New Question
                    </Link>
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent" asChild>
                    <Link href="/admin/categories/new">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Category
                    </Link>
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent" asChild>
                    <Link href="/admin/reports">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Generate Report
                    </Link>
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent" asChild>
                    <Link href="/admin/settings">
                      <Settings className="h-4 w-4 mr-2" />
                      System Settings
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
