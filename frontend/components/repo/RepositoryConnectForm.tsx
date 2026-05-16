"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";
import { createRepository, syncRepository } from "@/lib/api";
import { Repository } from "@/types/api";

interface RepositoryConnectFormProps {
  onSuccess?: (repo: Repository) => void;
}

export default function RepositoryConnectForm({ onSuccess }: RepositoryConnectFormProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [githubUrl, setGithubUrl] = useState("https://github.com/ISIS3510-MobileApps-Group42-202610/group-42-kotlin");
  const [branch, setBranch] = useState("main");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSyncStatus(null);

    if (!name.trim() || !githubUrl.trim()) {
      setError("Name and GitHub URL are required");
      return;
    }

    setIsSubmitting(true);

    try {
      // Create repository
      setSyncStatus("Creating repository...");
      const repo = await createRepository({
        name: name.trim(),
        description: description.trim() || undefined,
        github_url: githubUrl.trim(),
        default_branch: branch.trim() || "main",
      });

      // Sync repository
      setSyncStatus("Syncing repository files...");
      await syncRepository(repo.id);

      setSyncStatus("Repository connected successfully!");
      
      // Reset form
      setName("");
      setDescription("");
      setGithubUrl("https://github.com/ISIS3510-MobileApps-Group42-202610/group-42-kotlin");
      setBranch("main");

      // Call success callback
      if (onSuccess) {
        onSuccess(repo);
      }
    } catch (err) {
      console.error("Failed to connect repository:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to connect repository. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-2xl text-white">Connect Repository</CardTitle>
        <CardDescription className="text-slate-400">
          Connect a GitHub repository to analyze code changes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-white">
              Repository Name *
            </Label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="UniMarket"
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              disabled={isSubmitting}
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-white">
              Description
            </Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Android marketplace application"
              className="min-h-[80px] bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-blue-500"
              disabled={isSubmitting}
            />
          </div>

          {/* GitHub URL */}
          <div className="space-y-2">
            <Label htmlFor="githubUrl" className="text-white">
              GitHub URL *
            </Label>
            <input
              id="githubUrl"
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              disabled={isSubmitting}
              required
            />
          </div>

          {/* Branch */}
          <div className="space-y-2">
            <Label htmlFor="branch" className="text-white">
              Default Branch
            </Label>
            <input
              id="branch"
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              disabled={isSubmitting}
            />
          </div>

          {/* Sync Status */}
          {syncStatus && (
            <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-3">
              <p className="text-blue-300 text-sm">{syncStatus}</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-3">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting || !name.trim() || !githubUrl.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 text-lg"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Connecting...
              </>
            ) : (
              "Connect Repository"
            )}
          </Button>
        </form>

        {/* Info */}
        <div className="mt-4 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
          <p className="text-sm text-slate-400">
            <strong className="text-slate-300">Note:</strong> The repository will be cloned and indexed.
            This may take a few moments depending on the repository size.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// Made with Bob