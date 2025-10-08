import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BookOpen, Users, Trophy, BarChart3 } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="h-8 w-8 text-secondary" />
              <h1 className="text-2xl font-bold text-foreground">QuizMaster</h1>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" asChild>
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild>
                <Link href="/register">Sign Up</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <h2 className="text-4xl md:text-6xl font-bold text-foreground mb-6 text-balance">
            Master Your Competitive Exams
          </h2>
          <p className="text-xl text-muted-foreground mb-8 text-pretty">
            Practice with thousands of questions, track your progress, and ace your competitive exams with our
            comprehensive mock test platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/register">Start Practicing</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Login to Continue</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-card">
        <div className="container mx-auto max-w-6xl">
          <h3 className="text-3xl font-bold text-center text-foreground mb-12">Why Choose QuizMaster?</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <BookOpen className="h-12 w-12 text-secondary mb-4" />
                <CardTitle>Comprehensive Question Bank</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Access thousands of carefully curated questions across multiple categories and difficulty levels.
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Users className="h-12 w-12 text-secondary mb-4" />
                <CardTitle>Mock Tests</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Take timed mock tests that simulate real exam conditions to build confidence and speed.
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Trophy className="h-12 w-12 text-secondary mb-4" />
                <CardTitle>Performance Tracking</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Monitor your progress with detailed analytics and identify areas for improvement.
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <BarChart3 className="h-12 w-12 text-secondary mb-4" />
                <CardTitle>Detailed Results</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Get instant feedback with comprehensive result analysis and performance insights.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-4">
        <div className="container mx-auto text-center">
          <p className="text-muted-foreground">© 2024 QuizMaster. Built for competitive exam success.</p>
        </div>
      </footer>
    </div>
  )
}
