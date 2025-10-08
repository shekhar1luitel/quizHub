"use client"

import { useEffect, useState } from "react"
import { useParams, useSearchParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Trophy, Clock, CheckCircle, XCircle, RotateCcw, Home, BookOpen, Target } from "lucide-react"

// Mock questions data (same as quiz page)
const mockQuestions = [
  {
    id: 1,
    question: "What is the capital of France?",
    options: ["London", "Berlin", "Paris", "Madrid"],
    correctAnswer: 2,
    explanation: "Paris is the capital and most populous city of France.",
  },
  {
    id: 2,
    question: "Which planet is known as the Red Planet?",
    options: ["Venus", "Mars", "Jupiter", "Saturn"],
    correctAnswer: 1,
    explanation: "Mars is called the Red Planet due to its reddish appearance caused by iron oxide on its surface.",
  },
  {
    id: 3,
    question: "Who wrote the play 'Romeo and Juliet'?",
    options: ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
    correctAnswer: 1,
    explanation: "William Shakespeare wrote Romeo and Juliet, one of his most famous tragedies.",
  },
]

export default function QuizResultsPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const router = useRouter()
  const [results, setResults] = useState<any>(null)
  const [showExplanations, setShowExplanations] = useState(false)

  useEffect(() => {
    const data = searchParams.get("data")
    if (data) {
      try {
        const parsedResults = JSON.parse(decodeURIComponent(data))

        // Calculate score
        let correctAnswers = 0
        Object.entries(parsedResults.answers).forEach(([questionIndex, userAnswer]) => {
          const question = mockQuestions[Number.parseInt(questionIndex)]
          if (question && question.correctAnswer === userAnswer) {
            correctAnswers++
          }
        })

        const score = Math.round((correctAnswers / parsedResults.totalQuestions) * 100)

        setResults({
          ...parsedResults,
          correctAnswers,
          score,
          questions: mockQuestions,
        })
      } catch (error) {
        console.error("Error parsing results:", error)
        router.push("/dashboard")
      }
    } else {
      router.push("/dashboard")
    }
  }, [searchParams, router])

  if (!results) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading results...</p>
        </div>
      </div>
    )
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

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="h-8 w-8 text-secondary" />
              <h1 className="text-2xl font-bold text-foreground">Quiz Results</h1>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" asChild>
                <a href={`/quiz/${params.categoryId}`}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Retake Quiz
                </a>
              </Button>
              <Button asChild>
                <a href="/dashboard">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </a>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Score Overview */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-secondary/10 mb-4">
            <Trophy className={`h-12 w-12 ${getScoreColor(results.score)}`} />
          </div>
          <h2 className="text-4xl font-bold text-foreground mb-2">{results.score}%</h2>
          <p className="text-xl text-muted-foreground mb-4">
            {results.correctAnswers} out of {results.totalQuestions} correct
          </p>
          <Badge variant={getScoreBadgeVariant(results.score)} className="text-sm px-4 py-1">
            {results.score >= 80 ? "Excellent!" : results.score >= 60 ? "Good Job!" : "Keep Practicing!"}
          </Badge>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Score</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getScoreColor(results.score)}`}>{results.score}%</div>
              <Progress value={results.score} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Correct Answers</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{results.correctAnswers}</div>
              <p className="text-xs text-muted-foreground">out of {results.totalQuestions}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Wrong Answers</CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{results.totalQuestions - results.correctAnswers}</div>
              <p className="text-xs text-muted-foreground">questions missed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time Spent</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatTime(results.timeSpent)}</div>
              <p className="text-xs text-muted-foreground">total time</p>
            </CardContent>
          </Card>
        </div>

        {/* Question Review */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Question Review</CardTitle>
                <CardDescription>Review your answers and explanations</CardDescription>
              </div>
              <Button variant="outline" onClick={() => setShowExplanations(!showExplanations)}>
                {showExplanations ? "Hide" : "Show"} Explanations
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {results.questions.map((question: any, index: number) => {
                const userAnswer = results.answers[index]
                const isCorrect = userAnswer === question.correctAnswer
                const wasAnswered = userAnswer !== undefined

                return (
                  <div key={question.id} className="border border-border rounded-lg p-4">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="flex-shrink-0 mt-1">
                        {isCorrect ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : wasAnswered ? (
                          <XCircle className="h-5 w-5 text-red-600" />
                        ) : (
                          <div className="h-5 w-5 rounded-full border-2 border-muted-foreground" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-foreground mb-2">
                          Question {index + 1}: {question.question}
                        </h4>

                        <div className="space-y-2">
                          {question.options.map((option: string, optionIndex: number) => {
                            const isUserAnswer = userAnswer === optionIndex
                            const isCorrectAnswer = question.correctAnswer === optionIndex

                            return (
                              <div
                                key={optionIndex}
                                className={`p-2 rounded border text-sm ${
                                  isCorrectAnswer
                                    ? "border-green-300 bg-green-50 text-green-800"
                                    : isUserAnswer && !isCorrectAnswer
                                      ? "border-red-300 bg-red-50 text-red-800"
                                      : "border-border bg-background"
                                }`}
                              >
                                <span className="font-medium mr-2">{String.fromCharCode(65 + optionIndex)}.</span>
                                {option}
                                {isCorrectAnswer && (
                                  <Badge variant="outline" className="ml-2 text-xs bg-green-100 text-green-800">
                                    Correct
                                  </Badge>
                                )}
                                {isUserAnswer && !isCorrectAnswer && (
                                  <Badge variant="outline" className="ml-2 text-xs bg-red-100 text-red-800">
                                    Your Answer
                                  </Badge>
                                )}
                              </div>
                            )
                          })}
                        </div>

                        {showExplanations && question.explanation && (
                          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                            <p className="text-sm text-blue-800">
                              <strong>Explanation:</strong> {question.explanation}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mt-8 justify-center">
          <Button size="lg" asChild>
            <a href={`/quiz/${params.categoryId}`}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Take Quiz Again
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a href="/categories">
              <BookOpen className="h-4 w-4 mr-2" />
              Try Another Category
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a href="/dashboard">
              <Home className="h-4 w-4 mr-2" />
              Back to Dashboard
            </a>
          </Button>
        </div>
      </div>
    </div>
  )
}
