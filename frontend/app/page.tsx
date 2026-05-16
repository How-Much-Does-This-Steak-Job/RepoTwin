import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-6xl font-bold text-white mb-6">
              RepoTwin by Bob
            </h1>
            <p className="text-2xl text-slate-300 mb-8">
              Simulate the blast radius of a code change before writing code
            </p>
            <Link href="/demo">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 px-8 text-lg">
                Try Demo
              </Button>
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
            <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-white text-xl">🎯 Impact Analysis</CardTitle>
                <CardDescription className="text-slate-300">
                  Understand which files and modules will be affected by your proposed changes
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-white text-xl">⚠️ Risk Assessment</CardTitle>
                <CardDescription className="text-slate-300">
                  Identify potential risks, breaking changes, and regression points
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-white text-xl">🧪 Test Recommendations</CardTitle>
                <CardDescription className="text-slate-300">
                  Get comprehensive test plans and coverage recommendations
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-white text-xl">📋 Implementation Plan</CardTitle>
                <CardDescription className="text-slate-300">
                  Receive phased implementation strategies with rollback plans
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* IBM Bob Attribution */}
          <Card className="bg-blue-900/20 border-blue-700">
            <CardContent className="pt-6">
              <p className="text-blue-300 text-center">
                <strong>🤖 Powered by IBM Bob:</strong> Advanced AI-driven repository intelligence
                for safer, smarter development decisions.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Made with Bob