"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getAnalysisResults, generateShadowPRPreview } from "@/lib/api";
import { AnalysisResults, RiskLevel, ImpactLevel } from "@/types/api";
import { ShadowPRPreview as ShadowPRPreviewType } from "@/types/shadow-pr";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ShadowPRPreview } from "@/components/shadow-pr/ShadowPRPreview";
import { ShadowPRDownload } from "@/components/shadow-pr/ShadowPRDownload";
import {
  AlertCircle,
  CheckCircle2,
  FileCode,
  Loader2,
  Shield,
  TestTube,
  Copy,
  Check,
  TrendingUp,
  GitBranch,
  Zap,
  Target,
  Sparkles,
  Package
} from "lucide-react";

function ResultsContent() {
  const searchParams = useSearchParams();
  const analysisId = searchParams.get("analysisId");

  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [shadowPR, setShadowPR] = useState<ShadowPRPreviewType | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingShadowPR, setLoadingShadowPR] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!analysisId) {
      setError("No analysis ID provided");
      setLoading(false);
      return;
    }

    const loadResults = async () => {
      try {
        const data = await getAnalysisResults(analysisId);
        setResults(data);
        
        // Auto-generate Shadow PR preview
        try {
          setLoadingShadowPR(true);
          const shadowPRData = await generateShadowPRPreview(analysisId);
          setShadowPR(shadowPRData);
        } catch (shadowPRErr) {
          console.warn("Failed to load Shadow PR preview:", shadowPRErr);
          // Don't fail the whole page if Shadow PR fails
        } finally {
          setLoadingShadowPR(false);
        }
      } catch (err) {
        console.error("Failed to load results:", err);
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load analysis results"
        );
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [analysisId]);

  const handleGenerateShadowPR = async () => {
    if (!analysisId) return;
    
    setLoadingShadowPR(true);
    try {
      const shadowPRData = await generateShadowPRPreview(analysisId);
      setShadowPR(shadowPRData);
    } catch (err) {
      console.error("Failed to generate Shadow PR:", err);
    } finally {
      setLoadingShadowPR(false);
    }
  };

  const getRiskBadgeColor = (level: RiskLevel) => {
    switch (level) {
      case RiskLevel.LOW:
        return "bg-green-900/30 text-green-400 border-green-700";
      case RiskLevel.MEDIUM:
        return "bg-yellow-900/30 text-yellow-400 border-yellow-700";
      case RiskLevel.HIGH:
        return "bg-orange-900/30 text-orange-400 border-orange-700";
      case RiskLevel.CRITICAL:
        return "bg-red-900/30 text-red-400 border-red-700";
      default:
        return "bg-slate-900/30 text-slate-400 border-slate-700";
    }
  };

  const getImpactBadgeColor = (level: ImpactLevel) => {
    switch (level) {
      case ImpactLevel.DIRECT:
        return "bg-red-900/30 text-red-400 border-red-700";
      case ImpactLevel.INDIRECT:
        return "bg-yellow-900/30 text-yellow-400 border-yellow-700";
      case ImpactLevel.POTENTIAL:
        return "bg-blue-900/30 text-blue-400 border-blue-700";
      default:
        return "bg-slate-900/30 text-slate-400 border-slate-700";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-slate-300">Loading Shadow PR results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <Card className="bg-slate-900/50 border-slate-700 backdrop-blur max-w-md">
          <CardHeader>
            <CardTitle className="text-red-400">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-300">{error || "No results available"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getProviderLabel = (provider: string) => {
    switch (provider) {
      case "watsonx":
        return "watsonx.ai";
      case "heuristic":
        return "Heuristic Engine";
      case "sample":
        return "Sample Fallback";
      default:
        return provider;
    }
  };

  const getProviderBadgeColor = (provider: string) => {
    switch (provider) {
      case "watsonx":
        return "bg-purple-900/30 text-purple-400 border-purple-700";
      case "heuristic":
        return "bg-blue-900/30 text-blue-400 border-blue-700";
      case "sample":
        return "bg-slate-900/30 text-slate-400 border-slate-700";
      default:
        return "bg-slate-900/30 text-slate-400 border-slate-700";
    }
  };

  const copyPRBrief = async () => {
    const prBrief = `# Shadow PR Analysis

## ${results.summary.title}

${results.summary.overview}

### Key Points
${results.summary.key_points.map(point => `- ${point}`).join('\n')}

### Impact Metrics
- Files Affected: ${results.impact_radius.metrics.files_affected}
- Risk Score: ${results.risk_assessment.score}/100
- Risk Level: ${results.risk_assessment.overall_level.toUpperCase()}
- Implementation Effort: ${results.implementation_plan.total_estimated_effort}

### Analysis Provider
Provider: ${getProviderLabel(results.provider)}${results.enhanced_by_llm ? ' (AI Enhanced)' : ''}

---
Generated by RepoTwin - Built with IBM Bob IDE
`;

    try {
      await navigator.clipboard.writeText(prBrief);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header with Action Button */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <GitBranch className="h-8 w-8 text-blue-400" />
              Shadow PR Analysis
            </h1>
            <p className="text-lg text-slate-300">{results.summary.title}</p>
          </div>
          <Button
            onClick={copyPRBrief}
            className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="h-4 w-4 mr-2" />
                Copy PR Brief
              </>
            )}
          </Button>
        </div>

        {/* Analysis Provider Badge - Enhanced */}
        <Card className="bg-gradient-to-r from-slate-900/50 to-blue-900/30 border-slate-700 backdrop-blur mb-6 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <Zap className="h-5 w-5 text-blue-400" />
                <span className="text-slate-300 text-sm font-medium">Analysis Provider:</span>
                <Badge className={`text-sm px-3 py-1.5 font-semibold ${getProviderBadgeColor(results.provider)}`}>
                  {getProviderLabel(results.provider)}
                </Badge>
                {results.enhanced_by_llm && (
                  <Badge className="bg-green-900/30 text-green-400 border-green-700 text-sm px-3 py-1.5 font-semibold animate-pulse">
                    <Sparkles className="h-3 w-3 mr-1" />
                    AI Enhanced
                  </Badge>
                )}
              </div>
              <div className="text-sm text-slate-400 max-w-2xl">
                <p>
                  Built with <span className="text-blue-400 font-semibold">IBM Bob IDE</span>.
                  {results.provider === "watsonx" ? (
                    <> Runtime LLM: <span className="text-purple-400 font-semibold">watsonx.ai</span></>
                  ) : results.provider === "heuristic" ? (
                    <> Code analysis with optional <span className="text-purple-400 font-semibold">watsonx.ai</span></>
                  ) : (
                    <> Sample demonstration data</>
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Summary Card */}
        <Card className="bg-slate-900/50 border-slate-700 backdrop-blur mb-6">
          <CardHeader>
            <CardTitle className="text-2xl text-white">Overview</CardTitle>
            <CardDescription className="text-slate-300 text-base">
              {results.summary.overview}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {results.summary.key_points.map((point, index) => (
                <div key={index} className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-slate-300">{point}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Blast Radius Visualization */}
        <Card className="bg-slate-900/50 border-slate-700 backdrop-blur mb-6 shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl text-white flex items-center gap-2">
              <Target className="h-6 w-6 text-red-400" />
              Blast Radius Analysis
            </CardTitle>
            <CardDescription className="text-slate-300">
              Impact scope: <span className="font-semibold text-white">{results.impact_radius.category.toUpperCase()}</span> - 
              Affecting <span className="font-semibold text-white">{results.impact_radius.metrics.percentage_of_codebase.toFixed(1)}%</span> of codebase
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Direct Impact */}
              <div className="relative">
                <div className="absolute inset-0 bg-red-500/10 rounded-lg blur-xl"></div>
                <div className="relative bg-gradient-to-br from-red-900/40 to-red-800/20 border-2 border-red-700 rounded-lg p-6 text-center">
                  <div className="text-5xl font-bold text-red-400 mb-2">
                    {results.impact_radius.metrics.files_direct}
                  </div>
                  <div className="text-sm text-red-300 font-semibold mb-1">DIRECT IMPACT</div>
                  <div className="text-xs text-slate-400">Core files requiring changes</div>
                </div>
              </div>

              {/* Indirect Impact */}
              <div className="relative">
                <div className="absolute inset-0 bg-yellow-500/10 rounded-lg blur-xl"></div>
                <div className="relative bg-gradient-to-br from-yellow-900/40 to-yellow-800/20 border-2 border-yellow-700 rounded-lg p-6 text-center">
                  <div className="text-5xl font-bold text-yellow-400 mb-2">
                    {results.impact_radius.metrics.files_indirect}
                  </div>
                  <div className="text-sm text-yellow-300 font-semibold mb-1">INDIRECT IMPACT</div>
                  <div className="text-xs text-slate-400">Dependent files affected</div>
                </div>
              </div>

              {/* Total Scope */}
              <div className="relative">
                <div className="absolute inset-0 bg-blue-500/10 rounded-lg blur-xl"></div>
                <div className="relative bg-gradient-to-br from-blue-900/40 to-blue-800/20 border-2 border-blue-700 rounded-lg p-6 text-center">
                  <div className="text-5xl font-bold text-blue-400 mb-2">
                    {results.impact_radius.metrics.files_affected}
                  </div>
                  <div className="text-sm text-blue-300 font-semibold mb-1">TOTAL SCOPE</div>
                  <div className="text-xs text-slate-400">All affected files</div>
                </div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-2xl font-bold text-white mb-1">
                  {results.impact_radius.metrics.functions_affected}
                </div>
                <div className="text-xs text-slate-400">Functions</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-2xl font-bold text-white mb-1">
                  {results.impact_radius.metrics.classes_affected}
                </div>
                <div className="text-xs text-slate-400">Classes</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-2xl font-bold text-white mb-1">
                  {results.impact_radius.metrics.tests_affected}
                </div>
                <div className="text-xs text-slate-400">Tests</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-2xl font-bold text-white mb-1">
                  {results.implementation_plan.phases.length}
                </div>
                <div className="text-xs text-slate-400">Phases</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Score Card - Enhanced */}
        <Card className="bg-gradient-to-br from-slate-900/50 to-slate-800/30 border-slate-700 backdrop-blur mb-6 shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl text-white flex items-center gap-2">
              <Shield className="h-6 w-6 text-orange-400" />
              Risk Assessment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row items-center gap-8">
              {/* Risk Score Gauge */}
              <div className="relative w-48 h-48 flex-shrink-0">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="none"
                    className="text-slate-700"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={`${(results.risk_assessment.score / 100) * 502.4} 502.4`}
                    className={
                      results.risk_assessment.score < 30 ? "text-green-400" :
                      results.risk_assessment.score < 50 ? "text-yellow-400" :
                      results.risk_assessment.score < 75 ? "text-orange-400" :
                      "text-red-400"
                    }
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <div className="text-5xl font-bold text-white">
                    {results.risk_assessment.score}
                  </div>
                  <div className="text-sm text-slate-400">/ 100</div>
                </div>
              </div>

              {/* Risk Details */}
              <div className="flex-1">
                <div className="mb-4">
                  <Badge
                    className={`text-xl px-6 py-2 ${getRiskBadgeColor(
                      results.risk_assessment.overall_level
                    )}`}
                  >
                    {results.risk_assessment.overall_level.toUpperCase()} RISK
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-slate-300">
                    <TrendingUp className="h-4 w-4 text-blue-400" />
                    <span className="text-sm">
                      <span className="font-semibold">{results.risk_assessment.factors.length}</span> risk factors identified
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-300">
                    <FileCode className="h-4 w-4 text-blue-400" />
                    <span className="text-sm">
                      Estimated effort: <span className="font-semibold">{results.implementation_plan.total_estimated_effort}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Tabs */}
        <Tabs defaultValue="shadow-pr" className="space-y-4">
          <TabsList className="bg-slate-900/50 border border-slate-700">
            <TabsTrigger value="shadow-pr" className="data-[state=active]:bg-slate-800">
              <Package className="h-4 w-4 mr-2" />
              Shadow PR
            </TabsTrigger>
            <TabsTrigger value="files" className="data-[state=active]:bg-slate-800">
              <FileCode className="h-4 w-4 mr-2" />
              Affected Files
            </TabsTrigger>
            <TabsTrigger value="risks" className="data-[state=active]:bg-slate-800">
              <Shield className="h-4 w-4 mr-2" />
              Risk Assessment
            </TabsTrigger>
            <TabsTrigger value="tests" className="data-[state=active]:bg-slate-800">
              <TestTube className="h-4 w-4 mr-2" />
              Test Plan
            </TabsTrigger>
            <TabsTrigger value="implementation" className="data-[state=active]:bg-slate-800">
              Implementation
            </TabsTrigger>
          </TabsList>

          {/* Shadow PR Tab */}
          <TabsContent value="shadow-pr" className="space-y-6">
            {loadingShadowPR ? (
              <Card className="bg-slate-900/50 border-slate-700">
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
                    <p className="text-slate-300">Generating Shadow PR preview...</p>
                  </div>
                </CardContent>
              </Card>
            ) : shadowPR ? (
              <>
                <ShadowPRPreview preview={shadowPR} />
                <ShadowPRDownload
                  preview={shadowPR}
                  repositoryName="UniMarket"
                  changeDescription={results.summary.title}
                />
              </>
            ) : (
              <Card className="bg-slate-900/50 border-slate-700">
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Package className="h-12 w-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-300 mb-4">Shadow PR preview not available</p>
                    <Button
                      onClick={handleGenerateShadowPR}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Generate Shadow PR
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Affected Files Tab */}
          <TabsContent value="files" className="space-y-4">
            {results.affected_files.map((file, index) => (
              <Card key={index} className="bg-slate-900/50 border-slate-700 hover:border-slate-600 transition-colors">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg text-white font-mono">
                        {file.path}
                      </CardTitle>
                      <CardDescription className="text-slate-400 mt-2">
                        {file.reasoning}
                      </CardDescription>
                    </div>
                    <Badge className={getImpactBadgeColor(file.impact_level)}>
                      {file.impact_level}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-slate-400">Change Type</p>
                      <p className="text-white font-semibold">{file.change_type}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Lines Added</p>
                      <p className="text-green-400 font-semibold">+{file.lines_added}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Lines Removed</p>
                      <p className="text-red-400 font-semibold">-{file.lines_removed}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Complexity</p>
                      <p className="text-white font-semibold">{file.complexity_change}</p>
                    </div>
                  </div>
                  {file.risk_factors.length > 0 && (
                    <div>
                      <p className="text-sm text-slate-400 mb-2">Risk Factors:</p>
                      <div className="space-y-1">
                        {file.risk_factors.map((risk, riskIndex) => (
                          <div key={riskIndex} className="flex items-start gap-2">
                            <AlertCircle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-slate-300">{risk}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Risk Assessment Tab */}
          <TabsContent value="risks" className="space-y-4">
            {results.risk_assessment.factors.map((factor, index) => (
              <Card key={index} className="bg-slate-900/50 border-slate-700">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg text-white">{factor.name}</CardTitle>
                    <Badge className={getRiskBadgeColor(factor.level)}>
                      {factor.level}
                    </Badge>
                  </div>
                  <CardDescription className="text-slate-300">
                    {factor.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-400">Likelihood</p>
                      <p className="text-white font-semibold">{factor.likelihood}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Impact</p>
                      <p className="text-white font-semibold">{factor.impact}</p>
                    </div>
                  </div>
                  <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-3">
                    <p className="text-sm text-slate-400 mb-1">Mitigation Strategy:</p>
                    <p className="text-blue-300">{factor.mitigation}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Test Plan Tab */}
          <TabsContent value="tests" className="space-y-4">
            {results.test_recommendations.new_tests_needed.length > 0 && (
              <Card className="bg-slate-900/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">New Tests Needed</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {results.test_recommendations.new_tests_needed.map((test, index) => (
                    <div key={index} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                      <div className="flex items-start justify-between mb-2">
                        <p className="text-white font-semibold">{test.type}</p>
                        <Badge className={test.priority === "high" ? "bg-red-900/30 text-red-400" : "bg-yellow-900/30 text-yellow-400"}>
                          {test.priority}
                        </Badge>
                      </div>
                      <p className="text-slate-300 text-sm">{test.description}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Implementation Tab */}
          <TabsContent value="implementation" className="space-y-4">
            <Card className="bg-slate-900/50 border-slate-700 mb-4">
              <CardHeader>
                <CardTitle className="text-white">Implementation Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-slate-400">Total Effort</p>
                    <p className="text-white font-semibold text-lg">
                      {results.implementation_plan.total_estimated_effort}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Phases</p>
                    <p className="text-white font-semibold text-lg">
                      {results.implementation_plan.phases.length}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-400 mb-2">Rollback Strategy:</p>
                  <p className="text-slate-300">{results.implementation_plan.rollback_strategy}</p>
                </div>
              </CardContent>
            </Card>

            {results.implementation_plan.phases.map((phase, index) => (
              <Card key={index} className="bg-slate-900/50 border-slate-700">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-white">
                        Phase {phase.phase}: {phase.name}
                      </CardTitle>
                      <CardDescription className="text-slate-300 mt-2">
                        {phase.description}
                      </CardDescription>
                    </div>
                    <Badge className="bg-blue-900/30 text-blue-400">
                      {phase.estimated_effort}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Files to Modify:</p>
                    <div className="flex flex-wrap gap-2">
                      {phase.files.map((file, fileIndex) => (
                        <Badge key={fileIndex} variant="outline" className="font-mono text-xs">
                          {file}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Checkpoints:</p>
                    <div className="space-y-1">
                      {phase.checkpoints.map((checkpoint, cpIndex) => (
                        <div key={cpIndex} className="flex items-start gap-2">
                          <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-slate-300">{checkpoint}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>

        {/* IBM Bob Evidence Card */}
        <Card className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-blue-700 mt-6 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  🤖 Powered by IBM Bob IDE
                </h3>
                <p className="text-blue-300 text-sm leading-relaxed">
                  This Shadow PR analysis was generated using <span className="font-semibold">IBM Bob's advanced AI capabilities</span> to understand repository structure, predict change impact, and provide actionable insights for safer development.
                  {results.enhanced_by_llm && (
                    <> Enhanced with <span className="font-semibold text-purple-300">watsonx.ai</span> runtime LLM for deeper analysis.</>
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-slate-300">Loading Shadow PR results...</p>
        </div>
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}

// Made with Bob