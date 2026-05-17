"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Check, Loader2, Package } from "lucide-react";
import { ShadowPRPreview } from "@/types/shadow-pr";
import { downloadShadowPR, downloadShadowPRFile } from "@/lib/api";

interface ShadowPRDownloadProps {
  preview: ShadowPRPreview;
  repositoryName: string;
  changeDescription: string;
}

export function ShadowPRDownload({
  preview,
  repositoryName,
  changeDescription,
}: ShadowPRDownloadProps) {
  const [downloading, setDownloading] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const [downloadingFile, setDownloadingFile] = useState<string | null>(null);

  const handleDownloadComplete = async () => {
    setDownloading(true);
    try {
      await downloadShadowPR(preview, repositoryName, changeDescription);
      setDownloaded(true);
      setTimeout(() => setDownloaded(false), 3000);
    } catch (error) {
      console.error("Failed to download Shadow PR:", error);
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadFile = async (file: { path: string; content: string }) => {
    setDownloadingFile(file.path);
    try {
      await downloadShadowPRFile(file);
    } catch (error) {
      console.error("Failed to download file:", error);
    } finally {
      setDownloadingFile(null);
    }
  };

  return (
    <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-2xl text-white flex items-center gap-2">
          <Package className="h-6 w-6 text-blue-400" />
          Shadow PR Package
        </CardTitle>
        <CardDescription className="text-slate-300">
          Download the complete Shadow PR analysis package or individual files
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Complete Package Download */}
        <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-700 rounded-lg p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Complete Shadow PR Package
              </h3>
              <p className="text-sm text-slate-300">
                Includes PR brief, implementation plan, regression pack, and all analysis documents
              </p>
            </div>
            <Badge className="bg-blue-900/30 text-blue-400 border-blue-700">
              {preview.files_to_create.length} files
            </Badge>
          </div>
          <Button
            onClick={handleDownloadComplete}
            disabled={downloading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            {downloading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Preparing Download...
              </>
            ) : downloaded ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Downloaded!
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Download Complete Package
              </>
            )}
          </Button>
        </div>

        {/* Individual Files */}
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">Individual Files</h3>
          <div className="space-y-3">
            {preview.files_to_create.map((file, index) => (
              <div
                key={index}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="h-4 w-4 text-blue-400" />
                      <p className="text-white font-mono text-sm">{file.path}</p>
                    </div>
                    <p className="text-sm text-slate-400">{file.description}</p>
                  </div>
                  <Button
                    onClick={() => handleDownloadFile(file)}
                    disabled={downloadingFile === file.path}
                    className="flex-shrink-0 h-8 w-8 p-0 border border-slate-600 hover:bg-slate-700"
                  >
                    {downloadingFile === file.path ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <Download className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* PR Details */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">Shadow PR Details</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">Branch Name:</span>
              <span className="text-white font-mono">{preview.branch_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">PR Title:</span>
              <span className="text-white">{preview.pr_title}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Analysis ID:</span>
              <span className="text-white font-mono text-xs">{preview.analysis_id}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Made with Bob