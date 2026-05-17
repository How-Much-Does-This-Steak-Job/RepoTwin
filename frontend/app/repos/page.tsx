"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, RefreshCw } from "lucide-react";
import RepositoryConnectForm from "@/components/repo/RepositoryConnectForm";
import RepositoryList from "@/components/repo/RepositoryList";
import RepositoryFilesPreview from "@/components/repo/RepositoryFilesPreview";
import { getRepositories, getSelectedRepoId } from "@/lib/api";
import { Repository } from "@/types/api";

export default function ReposPage() {
  const router = useRouter();
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepoId, setSelectedRepoId] = useState<string | null>(null);
  const [viewingFilesRepoId, setViewingFilesRepoId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRepositories = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await getRepositories();
      setRepositories(result.items);
      
      // Load selected repo from localStorage
      const savedRepoId = getSelectedRepoId();
      if (savedRepoId) {
        setSelectedRepoId(savedRepoId);
      }
    } catch (err) {
      console.error("Failed to load repositories:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load repositories"
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRepositories();
  }, []);

  const handleRepoCreated = (repo: Repository) => {
    // Reload repositories
    loadRepositories();
  };

  const handleRepoSelected = (repoId: string) => {
    setSelectedRepoId(repoId);
  };

  const handleViewFiles = (repoId: string) => {
    setViewingFilesRepoId(repoId);
  };

  const selectedRepo = repositories?.find((r) => r.id === selectedRepoId);
  const viewingRepo = repositories?.find((r) => r.id === viewingFilesRepoId);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Link href="/">
              <Button className="mb-4 bg-slate-800 hover:bg-slate-700 text-white">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-white mb-2">
                  Repository Management
                </h1>
                <p className="text-lg text-slate-300">
                  Connect and manage repositories for analysis
                </p>
              </div>
              <Button
                onClick={loadRepositories}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </div>
          </div>

          {/* Selected Repository Banner */}
          {selectedRepo && (
            <div className="mb-8 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-300 mb-1">
                    Selected Repository for Analysis
                  </p>
                  <p className="text-xl font-semibold text-white">
                    {selectedRepo.name}
                  </p>
                </div>
                <Link href="/demo">
                  <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    Go to Demo
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column: Connect Form */}
            <div>
              <RepositoryConnectForm onSuccess={handleRepoCreated} />
            </div>

            {/* Right Column: Repository List */}
            <div>
              <div className="mb-4">
                <h2 className="text-2xl font-bold text-white mb-2">
                  Connected Repositories
                </h2>
                <p className="text-slate-400">
                  {isLoading
                    ? "Loading repositories..."
                    : `${repositories.length} ${repositories.length === 1 ? "repository" : "repositories"} connected`}
                </p>
              </div>

              {error && (
                <div className="mb-4 bg-red-900/20 border border-red-700 rounded-lg p-4">
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              )}

              {!isLoading && !error && (
                <RepositoryList
                  repositories={repositories}
                  selectedRepoId={selectedRepoId}
                  onSelect={handleRepoSelected}
                  onViewFiles={handleViewFiles}
                />
              )}
            </div>
          </div>

          {/* Files Preview */}
          {viewingRepo && (
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-white">
                  File Preview
                </h2>
                <Button
                  onClick={() => setViewingFilesRepoId(null)}
                  className="bg-slate-800 hover:bg-slate-700 text-white"
                >
                  Close Preview
                </Button>
              </div>
              <RepositoryFilesPreview
                repoId={viewingRepo.id}
                repoName={viewingRepo.name}
              />
            </div>
          )}

          {/* Info Box */}
          <div className="mt-8 bg-slate-900/50 border border-slate-700 rounded-lg p-6 backdrop-blur">
            <h3 className="text-lg font-semibold text-white mb-3">
              How it works
            </h3>
            <ol className="space-y-2 text-slate-300">
              <li className="flex gap-2">
                <span className="font-semibold text-blue-400">1.</span>
                <span>Connect a GitHub repository by providing its URL</span>
              </li>
              <li className="flex gap-2">
                <span className="font-semibold text-blue-400">2.</span>
                <span>The repository will be cloned and indexed automatically</span>
              </li>
              <li className="flex gap-2">
                <span className="font-semibold text-blue-400">3.</span>
                <span>Select a repository to use for change analysis</span>
              </li>
              <li className="flex gap-2">
                <span className="font-semibold text-blue-400">4.</span>
                <span>Go to the Demo page to analyze code changes</span>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob