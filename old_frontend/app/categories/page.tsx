"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BookOpen, Search, Play, ArrowLeft, Filter } from "lucide-react"
import Link from "next/link"

// Mock data - replace with actual API calls
const mockCategories = [
  {
    id: 1,
    name: "General Knowledge",
    icon: "🌍",
    totalQuestions: 500,
    completed: 45,
    description: "World geography, history, science, and current events",
    difficulty: "Mixed",
    subcategories: ["World Geography", "History", "Science", "Sports"],
  },
  {
    id: 2,
    name: "Aptitude",
    icon: "🧮",
    totalQuestions: 300,
    completed: 23,
    description: "Numerical reasoning, logical thinking, and problem solving",
    difficulty: "Medium",
    subcategories: ["Numerical", "Logical", "Verbal", "Abstract"],
  },
  {
    id: 3,
    name: "Reasoning",
    icon: "🧠",
    totalQuestions: 400,
    completed: 67,
    description: "Logical reasoning, pattern recognition, and analytical thinking",
    difficulty: "Hard",
    subcategories: ["Logical", "Analytical", "Critical", "Spatial"],
  },
  {
    id: 4,
    name: "English",
    icon: "📚",
    totalQuestions: 250,
    completed: 12,
    description: "Grammar, vocabulary, comprehension, and writing skills",
    difficulty: "Easy",
    subcategories: ["Grammar", "Vocabulary", "Reading", "Writing"],
  },
  {
    id: 5,
    name: "Current Affairs",
    icon: "📰",
    totalQuestions: 200,
    completed: 8,
    description: "Recent events, politics, economics, and social issues",
    difficulty: "Mixed",
    subcategories: ["Politics", "Economics", "Technology", "Sports"],
  },
  {
    id: 6,
    name: "Mathematics",
    icon: "📊",
    totalQuestions: 350,
    completed: 34,
    description: "Algebra, geometry, statistics, and advanced mathematics",
    difficulty: "Hard",
    subcategories: ["Algebra", "Geometry", "Statistics", "Calculus"],
  },
]

export default function CategoriesPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedDifficulty, setSelectedDifficulty] = useState("All")

  const filteredCategories = mockCategories.filter((category) => {
    const matchesSearch =
      category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      category.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDifficulty = selectedDifficulty === "All" || category.difficulty === selectedDifficulty
    return matchesSearch && matchesDifficulty
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Easy":
        return "bg-green-100 text-green-800"
      case "Medium":
        return "bg-yellow-100 text-yellow-800"
      case "Hard":
        return "bg-red-100 text-red-800"
      default:
        return "bg-blue-100 text-blue-800"
    }
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
                <BookOpen className="h-8 w-8 text-secondary" />
                <h1 className="text-2xl font-bold text-foreground">Practice Categories</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search categories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
            >
              <option value="All">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
              <option value="Mixed">Mixed</option>
            </select>
          </div>
        </div>

        {/* Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCategories.map((category) => (
            <Card key={category.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{category.icon}</span>
                    <div>
                      <CardTitle className="text-xl">{category.name}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={getDifficultyColor(category.difficulty)}>{category.difficulty}</Badge>
                        <span className="text-sm text-muted-foreground">
                          {category.completed}/{category.totalQuestions} completed
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-4">{category.description}</CardDescription>

                <Progress value={(category.completed / category.totalQuestions) * 100} className="mb-4" />

                <div className="mb-4">
                  <h4 className="text-sm font-medium text-foreground mb-2">Subcategories:</h4>
                  <div className="flex flex-wrap gap-1">
                    {category.subcategories.map((sub, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {sub}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button size="sm" className="flex-1" asChild>
                    <Link href={`/quiz/${category.id}`}>
                      <Play className="h-4 w-4 mr-2" />
                      Start Quiz
                    </Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <Link href={`/practice/${category.id}`}>Practice</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredCategories.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">No categories found</h3>
            <p className="text-muted-foreground">Try adjusting your search or filter criteria.</p>
          </div>
        )}
      </div>
    </div>
  )
}
