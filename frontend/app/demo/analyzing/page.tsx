"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getAnalysisProgress } from "@/lib/api";
import { AnalysisProgress } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";

function AnalyzingContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const analysisId = searchParams.get("analysisId");

  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      setError("No analysis ID provided");
      return;
    }

    let pollInterval: NodeJS.Timeout;

    const pollProgress = async () => {
      try {
        const progressData = await getAnalysisProgress(analysisId);
        setProgress(progressData);

        // Redirect to results when completed
        if (progressData.status === "completed") {
          clearInterval(pollInterval);
          setTimeout(() => {
            router.push(`/demo/results?analysisId=${analysisId}`);
          }, 1000);
        } else if (progressData.status === "failed") {
          clearInterval(pollInterval);
          setError(progressData.message || "Analysis failed. Please try again.");
        }
      } catch (err) {
        console.error("Failed to get progress:", err);
        clearInterval(pollInterval);
        setError(
          err instanceof Error
            ? err.message
            : "Failed to get analysis progress"
        );
      }
    };

    // Initial poll
    pollProgress();

    // Poll every 1 second
    pollInterval = setInterval(pollProgress, 1000);

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [analysisId, router]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <Card className="bg-slate-900/50 border-slate-700 backdrop-blur max-w-md">
          <CardHeader>
            <CardTitle className="text-red-400">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-300">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">
              Analyzing Impact
            </h1>
            <p className="text-lg text-slate-300">
              IBM Bob is analyzing your change request...
            </p>
          </div>

          {/* Progress Card */}
          <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-2xl text-white flex items-center gap-3">
                <Loader2 className="h-6 w-6 animate-spin text-blue-400" />
                {progress?.current_step || "Initializing..."}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Progress</span>
                  <span className="text-white font-semibold">
                    {progress?.progress_percent || 0}%
                  </span>
                </div>
                <Progress
                  value={progress?.progress_percent || 0}
                  className="h-3 bg-slate-800"
                />
              </div>

              {/* Status Message */}
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <p className="text-slate-300">
                  {progress?.message || "Starting analysis..."}
                </p>
              </div>

              {/* Estimated Time */}
              {progress?.estimated_time_remaining !== undefined &&
                progress.estimated_time_remaining > 0 && (
                  <div className="text-center">
                    <p className="text-sm text-slate-400">
                      Estimated time remaining:{" "}
                      <span className="text-white font-semibold">
                        {progress.estimated_time_remaining}s
                      </span>
                    </p>
                  </div>
                )}

              {/* Analysis Steps */}
              <div className="space-y-3">
                <p className="text-sm font-medium text-slate-300">
                  Analysis Pipeline:
                </p>
                <div className="space-y-2">
                  {[
                    { step: "Reading change request", threshold: 10 },
                    { step: "Loading repository context", threshold: 25 },
                    { step: "Mapping affected modules", threshold: 45 },
                    { step: "Calculating blast radius", threshold: 65 },
                    { step: "Building regression pack", threshold: 85 },
                    { step: "Preparing Shadow PR", threshold: 95 },
                  ].map(({ step, threshold }) => {
                    const isComplete =
                      (progress?.progress_percent || 0) >= threshold;
                    const isCurrent =
                      (progress?.progress_percent || 0) >= threshold - 15 &&
                      (progress?.progress_percent || 0) < threshold + 15;

                    return (
                      <div
                        key={step}
                        className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                          isComplete
                            ? "bg-blue-900/30 border border-blue-700"
                            : isCurrent
                            ? "bg-slate-800/50 border border-slate-600"
                            : "bg-slate-800/20 border border-slate-800"
                        }`}
                      >
                        <div
                          className={`w-2 h-2 rounded-full ${
                            isComplete
                              ? "bg-blue-400"
                              : isCurrent
                              ? "bg-yellow-400 animate-pulse"
                              : "bg-slate-600"
                          }`}
                        />
                        <span
                          className={`text-sm ${
                            isComplete
                              ? "text-blue-300"
                              : isCurrent
                              ? "text-white"
                              : "text-slate-500"
                          }`}
                        >
                          {step}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* IBM Bob Attribution */}
              <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                <p className="text-sm text-blue-300">
                  <strong>🤖 IBM Bob Intelligence:</strong> Using advanced AI
                  analysis to map dependencies, identify risks, and generate
                  comprehensive impact reports.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function AnalyzingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-slate-300">Loading...</p>
        </div>
      </div>
    }>
      <AnalyzingContent />
    </Suspense>
  );
}

// Made with Bob
