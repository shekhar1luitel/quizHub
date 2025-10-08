"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Clock, ChevronLeft, ChevronRight, Flag, CheckCircle, Circle, AlertTriangle, BookOpen } from "lucide-react"

// Mock data - replace with actual API calls
const mockQuizData = {
  id: 1,
  title: "General Knowledge Quiz",
  description: "Test your knowledge across various topics",
  timeLimit: 30, // minutes
  totalQuestions: 20,
  questions: [
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
    // Add more questions as needed
  ],
}

export default function QuizPage() {
  const params = useParams()
  const router = useRouter()
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<{ [key: number]: number }>({})
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<number>>(new Set())
  const [timeRemaining, setTimeRemaining] = useState(mockQuizData.timeLimit * 60) // in seconds
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showConfirmSubmit, setShowConfirmSubmit] = useState(false)

  // Timer effect
  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1)
      }, 1000)
      return () => clearTimeout(timer)
    } else {
      // Auto-submit when time runs out
      handleSubmitQuiz()
    }
  }, [timeRemaining])

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`
  }

  const handleAnswerSelect = (optionIndex: number) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion]: optionIndex,
    }))
  }

  const handleFlagQuestion = () => {
    setFlaggedQuestions((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(currentQuestion)) {
        newSet.delete(currentQuestion)
      } else {
        newSet.add(currentQuestion)
      }
      return newSet
    })
  }

  const handleNextQuestion = () => {
    if (currentQuestion < mockQuizData.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleQuestionNavigation = (questionIndex: number) => {
    setCurrentQuestion(questionIndex)
  }

  const handleSubmitQuiz = async () => {
    setIsSubmitting(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Calculate results
      const results = {
        answers,
        totalQuestions: mockQuizData.questions.length,
        timeSpent: mockQuizData.timeLimit * 60 - timeRemaining,
        categoryId: params.categoryId,
      }

      // Redirect to results page
      router.push(`/quiz/${params.categoryId}/results?data=${encodeURIComponent(JSON.stringify(results))}`)
    } catch (error) {
      console.error("Error submitting quiz:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getQuestionStatus = (index: number) => {
    if (answers[index] !== undefined) return "answered"
    if (flaggedQuestions.has(index)) return "flagged"
    return "unanswered"
  }

  const answeredCount = Object.keys(answers).length
  const progress = (answeredCount / mockQuizData.questions.length) * 100

  const currentQuestionData = mockQuizData.questions[currentQuestion]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BookOpen className="h-6 w-6 text-secondary" />
              <div>
                <h1 className="text-lg font-bold text-foreground">{mockQuizData.title}</h1>
                <p className="text-sm text-muted-foreground">
                  Question {currentQuestion + 1} of {mockQuizData.questions.length}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4" />
                <span className={`font-mono ${timeRemaining < 300 ? "text-destructive" : "text-foreground"}`}>
                  {formatTime(timeRemaining)}
                </span>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowConfirmSubmit(true)}
                disabled={isSubmitting}
              >
                Submit Quiz
              </Button>
            </div>
          </div>

          <div className="mt-4">
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {answeredCount} of {mockQuizData.questions.length} questions answered
            </p>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Question Panel */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-xl">Question {currentQuestion + 1}</CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleFlagQuestion}
                    className={flaggedQuestions.has(currentQuestion) ? "bg-yellow-100 border-yellow-300" : ""}
                  >
                    <Flag className="h-4 w-4 mr-2" />
                    {flaggedQuestions.has(currentQuestion) ? "Flagged" : "Flag"}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-lg text-foreground mb-6 leading-relaxed">{currentQuestionData.question}</p>

                <div className="space-y-3">
                  {currentQuestionData.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSelect(index)}
                      className={`w-full p-4 text-left border rounded-lg transition-colors ${
                        answers[currentQuestion] === index
                          ? "border-secondary bg-secondary/10 text-secondary-foreground"
                          : "border-border hover:border-secondary/50 hover:bg-accent"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex-shrink-0">
                          {answers[currentQuestion] === index ? (
                            <CheckCircle className="h-5 w-5 text-secondary" />
                          ) : (
                            <Circle className="h-5 w-5 text-muted-foreground" />
                          )}
                        </div>
                        <span className="text-sm font-medium mr-3 text-muted-foreground">
                          {String.fromCharCode(65 + index)}.
                        </span>
                        <span className="flex-1">{option}</span>
                      </div>
                    </button>
                  ))}
                </div>

                {/* Navigation Buttons */}
                <div className="flex items-center justify-between mt-8">
                  <Button variant="outline" onClick={handlePreviousQuestion} disabled={currentQuestion === 0}>
                    <ChevronLeft className="h-4 w-4 mr-2" />
                    Previous
                  </Button>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={handleFlagQuestion}
                      className={flaggedQuestions.has(currentQuestion) ? "bg-yellow-100 border-yellow-300" : ""}
                    >
                      <Flag className="h-4 w-4 mr-2" />
                      {flaggedQuestions.has(currentQuestion) ? "Unflag" : "Flag for Review"}
                    </Button>
                  </div>

                  <Button onClick={handleNextQuestion} disabled={currentQuestion === mockQuizData.questions.length - 1}>
                    Next
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Question Navigator */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="text-base">Question Navigator</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-2 mb-4">
                  {mockQuizData.questions.map((_, index) => {
                    const status = getQuestionStatus(index)
                    return (
                      <button
                        key={index}
                        onClick={() => handleQuestionNavigation(index)}
                        className={`aspect-square text-xs font-medium rounded border-2 transition-colors ${
                          index === currentQuestion
                            ? "border-secondary bg-secondary text-secondary-foreground"
                            : status === "answered"
                              ? "border-green-300 bg-green-100 text-green-800"
                              : status === "flagged"
                                ? "border-yellow-300 bg-yellow-100 text-yellow-800"
                                : "border-border bg-background hover:border-secondary/50"
                        }`}
                      >
                        {index + 1}
                      </button>
                    )
                  })}
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-green-300 bg-green-100 rounded"></div>
                    <span>Answered ({answeredCount})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-yellow-300 bg-yellow-100 rounded"></div>
                    <span>Flagged ({flaggedQuestions.size})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-border bg-background rounded"></div>
                    <span>Not Answered ({mockQuizData.questions.length - answeredCount})</span>
                  </div>
                </div>

                <Button
                  className="w-full mt-4"
                  variant="destructive"
                  onClick={() => setShowConfirmSubmit(true)}
                  disabled={isSubmitting}
                >
                  Submit Quiz
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Confirm Submit Dialog */}
      {showConfirmSubmit && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                Submit Quiz
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Alert className="mb-4">
                <AlertDescription>
                  You have answered {answeredCount} out of {mockQuizData.questions.length} questions.
                  {mockQuizData.questions.length - answeredCount > 0 && (
                    <span className="block mt-1 text-destructive">
                      {mockQuizData.questions.length - answeredCount} questions remain unanswered.
                    </span>
                  )}
                </AlertDescription>
              </Alert>

              <p className="text-sm text-muted-foreground mb-4">
                Are you sure you want to submit your quiz? This action cannot be undone.
              </p>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setShowConfirmSubmit(false)} className="flex-1">
                  Cancel
                </Button>
                <Button variant="destructive" onClick={handleSubmitQuiz} disabled={isSubmitting} className="flex-1">
                  {isSubmitting ? "Submitting..." : "Submit"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
