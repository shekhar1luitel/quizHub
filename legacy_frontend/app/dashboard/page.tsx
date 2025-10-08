"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen,
  Clock,
  Trophy,
  TrendingUp,
  Play,
  BarChart3,
  User,
  Settings,
  LogOut,
} from "lucide-react";
import Link from "next/link";

// Mock data - replace with actual API calls
const mockCategories = [
  {
    id: 1,
    name: "General Knowledge",
    icon: "🌍",
    totalQuestions: 500,
    completed: 45,
  },
  { id: 2, name: "Aptitude", icon: "🧮", totalQuestions: 300, completed: 23 },
  { id: 3, name: "Reasoning", icon: "🧠", totalQuestions: 400, completed: 67 },
  { id: 4, name: "English", icon: "📚", totalQuestions: 250, completed: 12 },
  {
    id: 5,
    name: "Current Affairs",
    icon: "📰",
    totalQuestions: 200,
    completed: 8,
  },
  {
    id: 6,
    name: "Mathematics",
    icon: "📊",
    totalQuestions: 350,
    completed: 34,
  },
];

const mockRecentTests = [
  {
    id: 1,
    name: "GK Mock Test #1",
    score: 85,
    totalQuestions: 50,
    date: "2024-01-15",
    duration: "45 min",
  },
  {
    id: 2,
    name: "Aptitude Practice",
    score: 72,
    totalQuestions: 30,
    date: "2024-01-14",
    duration: "30 min",
  },
  {
    id: 3,
    name: "Reasoning Quiz",
    score: 90,
    totalQuestions: 25,
    date: "2024-01-13",
    duration: "25 min",
  },
];

export default function DashboardPage() {
  const [user] = useState({ name: "John Doe", email: "john@example.com" });

  const totalCompleted = mockCategories.reduce(
    (sum, cat) => sum + cat.completed,
    0
  );
  const totalQuestions = mockCategories.reduce(
    (sum, cat) => sum + cat.totalQuestions,
    0
  );
  const overallProgress = Math.round((totalCompleted / totalQuestions) * 100);

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
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/profile">
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </Link>
              </Button>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/settings">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Link>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={async () => {
                  try {
                    await logout(); // call your logout API and clear token
                    window.location.href = "/"; // redirect to login/home page
                  } catch (err) {
                    console.error("Logout failed", err);
                  }
                }}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            Welcome back, {user.name}!
          </h2>
          <p className="text-muted-foreground">
            Ready to continue your learning journey?
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Progress
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overallProgress}%</div>
              <Progress value={overallProgress} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Questions Solved
              </CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalCompleted}</div>
              <p className="text-xs text-muted-foreground">
                out of {totalQuestions}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tests Taken</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockRecentTests.length}</div>
              <p className="text-xs text-muted-foreground">this week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Average Score
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(
                  mockRecentTests.reduce((sum, test) => sum + test.score, 0) /
                    mockRecentTests.length
                )}
                %
              </div>
              <p className="text-xs text-muted-foreground">last 3 tests</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Categories Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-foreground">
                Practice Categories
              </h3>
              <Button variant="outline" asChild>
                <Link href="/categories">View All</Link>
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockCategories.map((category) => (
                <Card
                  key={category.id}
                  className="hover:shadow-md transition-shadow"
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{category.icon}</span>
                        <div>
                          <CardTitle className="text-lg">
                            {category.name}
                          </CardTitle>
                          <CardDescription>
                            {category.completed}/{category.totalQuestions}{" "}
                            questions
                          </CardDescription>
                        </div>
                      </div>
                      <Badge variant="secondary">
                        {Math.round(
                          (category.completed / category.totalQuestions) * 100
                        )}
                        %
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Progress
                      value={
                        (category.completed / category.totalQuestions) * 100
                      }
                      className="mb-4"
                    />
                    <div className="flex gap-2">
                      <Button size="sm" asChild>
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
          </div>

          {/* Recent Activity Sidebar */}
          <div>
            <h3 className="text-2xl font-bold text-foreground mb-6">
              Recent Tests
            </h3>
            <div className="space-y-4">
              {mockRecentTests.map((test) => (
                <Card key={test.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{test.name}</CardTitle>
                      <Badge
                        variant={
                          test.score >= 80
                            ? "default"
                            : test.score >= 60
                            ? "secondary"
                            : "destructive"
                        }
                      >
                        {test.score}%
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <BookOpen className="h-3 w-3" />
                        {test.totalQuestions} questions
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {test.duration}
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      {test.date}
                    </p>
                  </CardContent>
                </Card>
              ))}

              <Button
                variant="outline"
                className="w-full bg-transparent"
                asChild
              >
                <Link href="/history">View All Results</Link>
              </Button>
            </div>

            {/* Quick Actions */}
            <div className="mt-8">
              <h4 className="text-lg font-semibold text-foreground mb-4">
                Quick Actions
              </h4>
              <div className="space-y-2">
                <Button className="w-full" asChild>
                  <Link href="/mock-test">
                    <Trophy className="h-4 w-4 mr-2" />
                    Take Mock Test
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  className="w-full bg-transparent"
                  asChild
                >
                  <Link href="/random-quiz">
                    <Play className="h-4 w-4 mr-2" />
                    Random Quiz
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  className="w-full bg-transparent"
                  asChild
                >
                  <Link href="/analytics">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    View Analytics
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
