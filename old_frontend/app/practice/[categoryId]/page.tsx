"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  RotateCcw,
  ArrowLeft,
  Lightbulb,
} from "lucide-react"
import Link from "next/link"

// Mock practice questions
const mockPracticeQuestions = [
  {
    id: 1,
    question: "What is the capital of France?",
    options: ["London", "Berlin", "Paris", "Madrid"],
    correctAnswer: 2,
    explanation:
      "Paris is the capital and most populous city of France, located in the north-central part of the country.",
    difficulty: "Easy",
  },
  {
    id: 2,
    question: "Which planet is known as the Red Planet?",
    options: ["Venus", "Mars", "Jupiter", "Saturn"],
    correctAnswer: 1,
    explanation:
      "Mars is called the Red Planet due to its reddish appearance caused by iron oxide (rust) on its surface.",
    difficulty: "Easy",
  },
  {
    id: 3,
    question: "Who wrote the play 'Romeo and Juliet'?",
    options: ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
    correctAnswer: 1,
    explanation: "William Shakespeare wrote Romeo and Juliet around 1594-1596. It's one of his most famous tragedies.",
    difficulty: "Medium",
  },
]

export default function PracticePage() {
  const params = useParams()
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)

  const currentQuestionData = mockPracticeQuestions[currentQuestion]

  const handleAnswerSelect = (optionIndex: number) => {
    if (!showResult) {
      setSelectedAnswer(optionIndex)
    }
  }

  const handleSubmitAnswer = () => {
    if (selectedAnswer !== null) {
      setShowResult(true)
      setShowExplanation(true)
    }
  }

  const handleNextQuestion = () => {
    if (currentQuestion < mockPracticeQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedAnswer(null)
      setShowResult(false)
      setShowExplanation(false)
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
      setSelectedAnswer(null)
      setShowResult(false)
      setShowExplanation(false)
    }
  }

  const handleTryAgain = () => {
    setSelectedAnswer(null)
    setShowResult(false)
    setShowExplanation(false)
  }

  const isCorrect = selectedAnswer === currentQuestionData.correctAnswer
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
                <Link href="/categories">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Categories
                </Link>
              </Button>
              <div className="flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-secondary" />
                <div>
                  <h1 className="text-lg font-bold text-foreground">Practice Mode</h1>
                  <p className="text-sm text-muted-foreground">
                    Question {currentQuestion + 1} of {mockPracticeQuestions.length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-xl mb-2">Question {currentQuestion + 1}</CardTitle>
                <Badge className={getDifficultyColor(currentQuestionData.difficulty)}>
                  {currentQuestionData.difficulty}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-lg text-foreground mb-6 leading-relaxed">{currentQuestionData.question}</p>

            <div className="space-y-3 mb-6">
              {currentQuestionData.options.map((option, index) => {
                let buttonClass = "w-full p-4 text-left border rounded-lg transition-colors "

                if (showResult) {
                  if (index === currentQuestionData.correctAnswer) {
                    buttonClass += "border-green-500 bg-green-50 text-green-800"
                  } else if (index === selectedAnswer && selectedAnswer !== currentQuestionData.correctAnswer) {
                    buttonClass += "border-red-500 bg-red-50 text-red-800"
                  } else {
                    buttonClass += "border-border bg-muted/30"
                  }
                } else if (selectedAnswer === index) {
                  buttonClass += "border-secondary bg-secondary/10 text-secondary-foreground"
                } else {
                  buttonClass += "border-border hover:border-secondary/50 hover:bg-accent"
                }

                return (
                  <button
                    key={index}
                    onClick={() => handleAnswerSelect(index)}
                    className={buttonClass}
                    disabled={showResult}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-muted-foreground">
                        {String.fromCharCode(65 + index)}.
                      </span>
                      <span className="flex-1">{option}</span>
                      {showResult && index === currentQuestionData.correctAnswer && (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      )}
                      {showResult &&
                        index === selectedAnswer &&
                        selectedAnswer !== currentQuestionData.correctAnswer && (
                          <XCircle className="h-5 w-5 text-red-600" />
                        )}
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Result Alert */}
            {showResult && (
              <Alert className={`mb-6 ${isCorrect ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}`}>
                <div className="flex items-center gap-2">
                  {isCorrect ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <AlertDescription className={isCorrect ? "text-green-800" : "text-red-800"}>
                    {isCorrect ? "Correct! Well done." : "Incorrect. The correct answer is highlighted above."}
                  </AlertDescription>
                </div>
              </Alert>
            )}

            {/* Explanation */}
            {showExplanation && (
              <Card className="mb-6 bg-blue-50 border-blue-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2 text-blue-800">
                    <Lightbulb className="h-4 w-4" />
                    Explanation
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-blue-800">{currentQuestionData.explanation}</p>
                </CardContent>
              </Card>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <Button variant="outline" onClick={handlePreviousQuestion} disabled={currentQuestion === 0}>
                <ChevronLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>

              <div className="flex gap-2">
                {!showResult ? (
                  <Button onClick={handleSubmitAnswer} disabled={selectedAnswer === null}>
                    Submit Answer
                  </Button>
                ) : (
                  <>
                    <Button variant="outline" onClick={handleTryAgain}>
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Try Again
                    </Button>
                    {currentQuestion < mockPracticeQuestions.length - 1 && (
                      <Button onClick={handleNextQuestion}>
                        Next Question
                        <ChevronRight className="h-4 w-4 ml-2" />
                      </Button>
                    )}
                  </>
                )}
              </div>

              {currentQuestion === mockPracticeQuestions.length - 1 && showResult && (
                <Button asChild>
                  <Link href="/categories">Finish Practice</Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Progress Indicator */}
        <div className="mt-6 text-center">
          <div className="flex justify-center gap-2">
            {mockPracticeQuestions.map((_, index) => (
              <div
                key={index}
                className={`w-3 h-3 rounded-full ${
                  index === currentQuestion ? "bg-secondary" : index < currentQuestion ? "bg-green-500" : "bg-muted"
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Question {currentQuestion + 1} of {mockPracticeQuestions.length}
          </p>
        </div>
      </div>
    </div>
  )
}
