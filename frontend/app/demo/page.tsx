"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createAnalysis } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

export default function DemoPage() {
  const router = useRouter();
  const [changeRequest, setChangeRequest] = useState(
    "Add reservation flow before purchase."
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (changeRequest.trim().length < 10) {
      setError("Change request must be at least 10 characters long");
      return;
    }

    setIsSubmitting(true);

    try {
      // Create analysis with UniMarket demo repo
      const analysis = await createAnalysis({
        repo_id: "660e8400-e29b-41d4-a716-446655440000",
        change_description: changeRequest.trim(),
        target_branch: "main",
      });

      // Redirect to analyzing page
      router.push(`/demo/analyzing?analysisId=${analysis.id}`);
    } catch (err) {
      console.error("Failed to create analysis:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create analysis. Please try again."
      );
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">
              RepoTwin Demo
            </h1>
            <p className="text-lg text-slate-300">
              Simulate the blast radius of a code change before writing code
            </p>
          </div>

          {/* Demo Card */}
          <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-2xl text-white">
                Analyze Change Impact
              </CardTitle>
              <CardDescription className="text-slate-400">
                Enter a natural language description of your proposed code change.
                We'll analyze its impact across the UniMarket repository.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Repository Info */}
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-300">
                        Repository
                      </p>
                      <p className="text-lg font-semibold text-white">
                        UniMarket
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-300">
                        Branch
                      </p>
                      <p className="text-lg font-semibold text-white">main</p>
                    </div>
                  </div>
                </div>

                {/* Change Request Input */}
                <div className="space-y-2">
                  <Label htmlFor="changeRequest" className="text-white">
                    Change Request
                  </Label>
                  <Textarea
                    id="changeRequest"
                    value={changeRequest}
                    onChange={(e) => setChangeRequest(e.target.value)}
                    placeholder="Describe the change you want to make..."
                    className="min-h-[150px] bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-blue-500"
                    disabled={isSubmitting}
                  />
                  <p className="text-sm text-slate-400">
                    Example: "Add reservation flow before purchase" or "Implement
                    user authentication with OAuth"
                  </p>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                {/* Submit Button */}
                <Button
                  type="submit"
                  disabled={isSubmitting || changeRequest.trim().length < 10}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 text-lg"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Creating Analysis...
                    </>
                  ) : (
                    "Analyze Impact"
                  )}
                </Button>
              </form>

              {/* Info Box */}
              <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                <p className="text-sm text-blue-300">
                  <strong>💡 Powered by IBM Bob:</strong> This analysis uses
                  IBM Bob's AI capabilities to understand your repository
                  structure and predict the impact of your proposed changes.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
                <div className="text-3xl mb-2">🎯</div>
                <h3 className="text-white font-semibold mb-2">
                  Affected Files
                </h3>
                <p className="text-sm text-slate-400">
                  See exactly which files will be impacted by your change
                </p>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
                <div className="text-3xl mb-2">⚠️</div>
                <h3 className="text-white font-semibold mb-2">Risk Analysis</h3>
                <p className="text-sm text-slate-400">
                  Understand potential risks and breaking changes
                </p>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
                <div className="text-3xl mb-2">🧪</div>
                <h3 className="text-white font-semibold mb-2">Test Plan</h3>
                <p className="text-sm text-slate-400">
                  Get recommendations for regression testing
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
