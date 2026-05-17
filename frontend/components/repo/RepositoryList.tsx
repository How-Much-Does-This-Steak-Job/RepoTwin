"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, ExternalLink, FileCode2, GitBranch } from "lucide-react";
import { Repository } from "@/types/api";
import { setSelectedRepoId } from "@/lib/api";

interface RepositoryListProps {
  repositories: Repository[];
  selectedRepoId: string | null;
  onSelect?: (repoId: string) => void;
  onViewFiles?: (repoId: string) => void;
}

export default function RepositoryList({
  repositories,
  selectedRepoId,
  onSelect,
  onViewFiles,
}: RepositoryListProps) {
  const handleSelect = (repoId: string) => {
    setSelectedRepoId(repoId);
    if (onSelect) {
      onSelect(repoId);
    }
  };

  if (repositories.length === 0) {
    return (
      <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <FileCode2 className="mx-auto h-12 w-12 text-slate-600 mb-4" />
            <p className="text-slate-400">No repositories connected yet</p>
            <p className="text-sm text-slate-500 mt-2">
              Connect your first repository to get started
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {repositories.map((repo) => {
        const isSelected = repo.id === selectedRepoId;
        
        return (
          <Card
            key={repo.id}
            className={`bg-slate-900/50 border backdrop-blur transition-all ${
              isSelected
                ? "border-blue-500 ring-2 ring-blue-500/20"
                : "border-slate-700 hover:border-slate-600"
            }`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <CardTitle className="text-xl text-white">
                      {repo.name}
                    </CardTitle>
                    {isSelected && (
                      <Badge className="bg-blue-600 text-white">
                        Selected
                      </Badge>
                    )}
                    {repo.is_synced ? (
                      <Badge variant="outline" className="border-green-700 text-green-400">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Synced
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-yellow-700 text-yellow-400">
                        <Circle className="h-3 w-3 mr-1" />
                        Not Synced
                      </Badge>
                    )}
                  </div>
                  {repo.description && (
                    <CardDescription className="text-slate-400">
                      {repo.description}
                    </CardDescription>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Repository Info */}
                <div className="flex flex-wrap gap-4 text-sm">
                  <div className="flex items-center gap-2 text-slate-400">
                    <GitBranch className="h-4 w-4" />
                    <span>{repo.default_branch}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400">
                    <FileCode2 className="h-4 w-4" />
                    <span>{repo.file_count} files</span>
                  </div>
                  {repo.last_synced_at && (
                    <div className="text-slate-500 text-xs">
                      Last synced: {new Date(repo.last_synced_at).toLocaleString()}
                    </div>
                  )}
                </div>

                {/* GitHub URL */}
                <div className="flex items-center gap-2">
                  <a
                    href={repo.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                  >
                    {repo.github_url}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  {!isSelected && (
                    <Button
                      onClick={() => handleSelect(repo.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Select for Analysis
                    </Button>
                  )}
                  {repo.is_synced && onViewFiles && (
                    <Button
                      onClick={() => onViewFiles(repo.id)}
                      className="border border-slate-600 text-slate-300 hover:bg-slate-800 bg-transparent"
                    >
                      View Files
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

// Made with Bob