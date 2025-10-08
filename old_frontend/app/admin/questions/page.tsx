"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Search, Plus, Edit, Trash2, ArrowLeft, Eye, CheckCircle, XCircle, AlertTriangle } from "lucide-react"
import Link from "next/link"

// Mock questions data
const mockQuestions = [
  {
    id: 1,
    question: "What is the capital of France?",
    category: "General Knowledge",
    difficulty: "Easy",
    options: ["London", "Berlin", "Paris", "Madrid"],
    correctAnswer: 2,
    status: "active",
    createdBy: "Admin",
    createdAt: "2024-01-15",
    timesUsed: 245,
  },
  {
    id: 2,
    question: "Which planet is known as the Red Planet?",
    category: "General Knowledge",
    difficulty: "Easy",
    options: ["Venus", "Mars", "Jupiter", "Saturn"],
    correctAnswer: 1,
    status: "active",
    createdBy: "Admin",
    createdAt: "2024-01-14",
    timesUsed: 189,
  },
  {
    id: 3,
    question: "What is the derivative of x²?",
    category: "Mathematics",
    difficulty: "Medium",
    options: ["x", "2x", "x²", "2x²"],
    correctAnswer: 1,
    status: "draft",
    createdBy: "John Doe",
    createdAt: "2024-01-13",
    timesUsed: 0,
  },
  {
    id: 4,
    question: "Who wrote 'To Kill a Mockingbird'?",
    category: "English",
    difficulty: "Medium",
    options: ["Harper Lee", "Mark Twain", "Ernest Hemingway", "F. Scott Fitzgerald"],
    correctAnswer: 0,
    status: "review",
    createdBy: "Jane Smith",
    createdAt: "2024-01-12",
    timesUsed: 0,
  },
]

export default function AdminQuestionsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [selectedDifficulty, setSelectedDifficulty] = useState("All")
  const [selectedStatus, setSelectedStatus] = useState("All")

  const categories = ["All", ...Array.from(new Set(mockQuestions.map((q) => q.category)))]
  const difficulties = ["All", "Easy", "Medium", "Hard"]
  const statuses = ["All", "active", "draft", "review", "inactive"]

  const filteredQuestions = mockQuestions.filter((question) => {
    const matchesSearch =
      question.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      question.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "All" || question.category === selectedCategory
    const matchesDifficulty = selectedDifficulty === "All" || question.difficulty === selectedDifficulty
    const matchesStatus = selectedStatus === "All" || question.status === selectedStatus
    return matchesSearch && matchesCategory && matchesDifficulty && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "draft":
        return "bg-gray-100 text-gray-800"
      case "review":
        return "bg-yellow-100 text-yellow-800"
      case "inactive":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "draft":
        return <Edit className="h-4 w-4 text-gray-600" />
      case "review":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case "inactive":
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return null
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Easy":
        return "bg-green-100 text-green-800"
      case "Medium":
        return "bg-yellow-100 text-yellow-800"
      case "Hard":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
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
                <Link href="/admin">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div className="flex items-center gap-2">
                <BookOpen className="h-8 w-8 text-secondary" />
                <h1 className="text-2xl font-bold text-foreground">Question Management</h1>
              </div>
            </div>
            <Button asChild>
              <Link href="/admin/questions/new">
                <Plus className="h-4 w-4 mr-2" />
                Add Question
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Questions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockQuestions.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Active</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {mockQuestions.filter((q) => q.status === "active").length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {mockQuestions.filter((q) => q.status === "review").length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Drafts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">
                {mockQuestions.filter((q) => q.status === "draft").length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Filter & Search</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
              <div className="relative lg:col-span-2">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search questions..."
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
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                {difficulties.map((difficulty) => (
                  <option key={difficulty} value={difficulty}>
                    {difficulty === "All" ? "All Difficulties" : difficulty}
                  </option>
                ))}
              </select>

              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                {statuses.map((status) => (
                  <option key={status} value={status}>
                    {status === "All" ? "All Statuses" : status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
              </select>

              <Button
                variant="outline"
                onClick={() => {
                  setSearchTerm("")
                  setSelectedCategory("All")
                  setSelectedDifficulty("All")
                  setSelectedStatus("All")
                }}
              >
                Clear
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.map((question) => (
            <Card key={question.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(question.status)}
                      <h3 className="text-lg font-semibold text-foreground">{question.question}</h3>
                    </div>

                    <div className="flex items-center gap-4 mb-3">
                      <Badge className={getDifficultyColor(question.difficulty)}>{question.difficulty}</Badge>
                      <Badge className={getStatusColor(question.status)}>{question.status}</Badge>
                      <span className="text-sm text-muted-foreground">{question.category}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 mb-3">
                      {question.options.map((option, index) => (
                        <div
                          key={index}
                          className={`p-2 text-sm rounded border ${
                            index === question.correctAnswer
                              ? "border-green-300 bg-green-50 text-green-800"
                              : "border-border bg-muted/30"
                          }`}
                        >
                          <span className="font-medium mr-2">{String.fromCharCode(65 + index)}.</span>
                          {option}
                        </div>
                      ))}
                    </div>

                    <div className="flex items-center gap-6 text-xs text-muted-foreground">
                      <span>Created by {question.createdBy}</span>
                      <span>Created on {question.createdAt}</span>
                      <span>Used {question.timesUsed} times</span>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button size="sm" variant="outline">
                      <Eye className="h-4 w-4 mr-2" />
                      Preview
                    </Button>
                    <Button size="sm" variant="outline">
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    <Button size="sm" variant="outline" className="text-red-600 hover:text-red-700 bg-transparent">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredQuestions.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No questions found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || selectedCategory !== "All" || selectedDifficulty !== "All" || selectedStatus !== "All"
                  ? "Try adjusting your search or filter criteria."
                  : "Get started by creating your first question."}
              </p>
              <Button asChild>
                <Link href="/admin/questions/new">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Question
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
