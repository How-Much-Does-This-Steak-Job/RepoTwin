"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileCode2, Folder, Loader2 } from "lucide-react";
import { getRepositoryFiles } from "@/lib/api";
import { RepositoryFile } from "@/types/api";

interface RepositoryFilesPreviewProps {
  repoId: string;
  repoName: string;
}

export default function RepositoryFilesPreview({
  repoId,
  repoName,
}: RepositoryFilesPreviewProps) {
  const [files, setFiles] = useState<RepositoryFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadFiles = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await getRepositoryFiles(repoId);
        setFiles(result.files);
      } catch (err) {
        console.error("Failed to load files:", err);
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load repository files"
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadFiles();
  }, [repoId]);

  const getLanguageBadgeColor = (language?: string) => {
    if (!language) return "bg-slate-700 text-slate-300";
    
    const colors: Record<string, string> = {
      kotlin: "bg-purple-700 text-purple-100",
      java: "bg-orange-700 text-orange-100",
      javascript: "bg-yellow-700 text-yellow-100",
      typescript: "bg-blue-700 text-blue-100",
      python: "bg-green-700 text-green-100",
      xml: "bg-red-700 text-red-100",
      json: "bg-slate-700 text-slate-100",
    };

    return colors[language.toLowerCase()] || "bg-slate-700 text-slate-300";
  };

  return (
    <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-xl text-white">
          Repository Files: {repoName}
        </CardTitle>
        <CardDescription className="text-slate-400">
          {isLoading
            ? "Loading files..."
            : `${files.length} files indexed`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && files.length === 0 && (
          <div className="text-center py-8">
            <FileCode2 className="mx-auto h-12 w-12 text-slate-600 mb-4" />
            <p className="text-slate-400">No files found</p>
          </div>
        )}

        {!isLoading && !error && files.length > 0 && (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {files.slice(0, 100).map((file, index) => (
              <div
                key={`${file.path}-${index}`}
                className="flex items-center justify-between p-2 rounded bg-slate-800/50 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {file.type === "directory" ? (
                    <Folder className="h-4 w-4 text-blue-400 flex-shrink-0" />
                  ) : (
                    <FileCode2 className="h-4 w-4 text-slate-400 flex-shrink-0" />
                  )}
                  <span className="text-sm text-slate-300 truncate">
                    {file.path}
                  </span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {file.language && (
                    <Badge className={`text-xs ${getLanguageBadgeColor(file.language)}`}>
                      {file.language}
                    </Badge>
                  )}
                  {file.size !== undefined && (
                    <span className="text-xs text-slate-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  )}
                </div>
              </div>
            ))}
            {files.length > 100 && (
              <div className="text-center py-2">
                <p className="text-sm text-slate-500">
                  Showing 100 of {files.length} files
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Made with Bob