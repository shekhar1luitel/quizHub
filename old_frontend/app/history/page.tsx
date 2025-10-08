"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BookOpen, Search, Calendar, Clock, Trophy, TrendingUp, ArrowLeft, Eye, BarChart3 } from "lucide-react"
import Link from "next/link"

// Mock history data
const mockHistory = [
  {
    id: 1,
    title: "General Knowledge Quiz",
    category: "General Knowledge",
    categoryId: 1,
    score: 85,
    totalQuestions: 20,
    correctAnswers: 17,
    timeSpent: 1800, // seconds
    date: "2024-01-15T10:30:00Z",
    type: "quiz",
    difficulty: "Mixed",
  },
  {
    id: 2,
    title: "Aptitude Practice Test",
    category: "Aptitude",
    categoryId: 2,
    score: 72,
    totalQuestions: 15,
    correctAnswers: 11,
    timeSpent: 1200,
    date: "2024-01-14T14:20:00Z",
    type: "practice",
    difficulty: "Medium",
  },
  {
    id: 3,
    title: "Reasoning Mock Test",
    category: "Reasoning",
    categoryId: 3,
    score: 90,
    totalQuestions: 25,
    correctAnswers: 23,
    timeSpent: 2100,
    date: "2024-01-13T09:15:00Z",
    type: "mock",
    difficulty: "Hard",
  },
  {
    id: 4,
    title: "English Grammar Quiz",
    category: "English",
    categoryId: 4,
    score: 68,
    totalQuestions: 18,
    correctAnswers: 12,
    timeSpent: 1500,
    date: "2024-01-12T16:45:00Z",
    type: "quiz",
    difficulty: "Easy",
  },
  {
    id: 5,
    title: "Current Affairs Test",
    category: "Current Affairs",
    categoryId: 5,
    score: 78,
    totalQuestions: 22,
    correctAnswers: 17,
    timeSpent: 1650,
    date: "2024-01-11T11:30:00Z",
    type: "quiz",
    difficulty: "Mixed",
  },
  {
    id: 6,
    title: "Mathematics Practice",
    category: "Mathematics",
    categoryId: 6,
    score: 82,
    totalQuestions: 20,
    correctAnswers: 16,
    timeSpent: 2400,
    date: "2024-01-10T13:20:00Z",
    type: "practice",
    difficulty: "Hard",
  },
]

export default function HistoryPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [selectedType, setSelectedType] = useState("All")
  const [sortBy, setSortBy] = useState("date")

  const categories = ["All", ...Array.from(new Set(mockHistory.map((item) => item.category)))]
  const types = ["All", "quiz", "practice", "mock"]

  const filteredHistory = mockHistory
    .filter((item) => {
      const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = selectedCategory === "All" || item.category === selectedCategory
      const matchesType = selectedType === "All" || item.type === selectedType
      return matchesSearch && matchesCategory && matchesType
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "date":
          return new Date(b.date).getTime() - new Date(a.date).getTime()
        case "score":
          return b.score - a.score
        case "title":
          return a.title.localeCompare(b.title)
        default:
          return 0
      }
    })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return "default"
    if (score >= 60) return "secondary"
    return "destructive"
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "quiz":
        return "bg-blue-100 text-blue-800"
      case "practice":
        return "bg-green-100 text-green-800"
      case "mock":
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  // Calculate stats
  const totalTests = mockHistory.length
  const averageScore = Math.round(mockHistory.reduce((sum, test) => sum + test.score, 0) / totalTests)
  const totalTimeSpent = mockHistory.reduce((sum, test) => sum + test.timeSpent, 0)
  const bestScore = Math.max(...mockHistory.map((test) => test.score))

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
                <h1 className="text-2xl font-bold text-foreground">Quiz History</h1>
              </div>
            </div>
            <Button asChild>
              <Link href="/analytics">
                <TrendingUp className="h-4 w-4 mr-2" />
                View Analytics
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalTests}</div>
              <p className="text-xs text-muted-foreground">completed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getScoreColor(averageScore)}`}>{averageScore}%</div>
              <Progress value={averageScore} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Best Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getScoreColor(bestScore)}`}>{bestScore}%</div>
              <p className="text-xs text-muted-foreground">personal best</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time Spent</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Math.round(totalTimeSpent / 3600)}h</div>
              <p className="text-xs text-muted-foreground">total study time</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Filter & Search</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tests..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category === "All" ? "All Categories" : category}
                  </option>
                ))}
              </select>

              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                {types.map((type) => (
                  <option key={type} value={type}>
                    {type === "All" ? "All Types" : type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="date">Sort by Date</option>
                <option value="score">Sort by Score</option>
                <option value="title">Sort by Title</option>
              </select>

              <Button
                variant="outline"
                onClick={() => {
                  setSearchTerm("")
                  setSelectedCategory("All")
                  setSelectedType("All")
                  setSortBy("date")
                }}
              >
                Clear Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* History List */}
        <div className="space-y-4">
          {filteredHistory.map((test) => (
            <Card key={test.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-foreground">{test.title}</h3>
                      <Badge className={getTypeColor(test.type)}>{test.type}</Badge>
                      <Badge variant="outline">{test.difficulty}</Badge>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-muted-foreground mb-3">
                      <div className="flex items-center gap-1">
                        <BookOpen className="h-4 w-4" />
                        {test.category}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(test.date)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {formatTime(test.timeSpent)}
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Score:</span>
                        <Badge variant={getScoreBadgeVariant(test.score)} className="font-bold">
                          {test.score}%
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Questions:</span>
                        <span className="text-sm font-medium">
                          {test.correctAnswers}/{test.totalQuestions}
                        </span>
                      </div>
                      <Progress value={test.score} className="flex-1 max-w-32" />
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button size="sm" variant="outline" asChild>
                      <Link href={`/quiz/${test.categoryId}/results?data=${encodeURIComponent(JSON.stringify(test))}`}>
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Link>
                    </Button>
                    <Button size="sm" asChild>
                      <Link href={`/quiz/${test.categoryId}`}>Retake</Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredHistory.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No tests found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || selectedCategory !== "All" || selectedType !== "All"
                  ? "Try adjusting your search or filter criteria."
                  : "You haven't taken any tests yet. Start practicing to see your history here."}
              </p>
              <Button asChild>
                <Link href="/categories">Start Practicing</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
