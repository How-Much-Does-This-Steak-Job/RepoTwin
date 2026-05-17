"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GitBranch, FileText, Copy, Check } from "lucide-react";
import { ShadowPRPreview as ShadowPRPreviewType } from "@/types/shadow-pr";
import { useState } from "react";

interface ShadowPRPreviewProps {
  preview: ShadowPRPreviewType;
}

export function ShadowPRPreview({ preview }: ShadowPRPreviewProps) {
  const [copiedPRBody, setCopiedPRBody] = useState(false);
  const [copiedFile, setCopiedFile] = useState<string | null>(null);

  const copyPRBody = async () => {
    try {
      await navigator.clipboard.writeText(preview.pr_body);
      setCopiedPRBody(true);
      setTimeout(() => setCopiedPRBody(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const copyFileContent = async (path: string, content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFile(path);
      setTimeout(() => setCopiedFile(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <Card className="bg-slate-900/50 border-slate-700 backdrop-blur">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-2xl text-white flex items-center gap-2 mb-2">
              <GitBranch className="h-6 w-6 text-blue-400" />
              Shadow PR Preview
            </CardTitle>
            <CardDescription className="text-slate-300 text-base">
              {preview.summary}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* PR Metadata */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-3">
          <div>
            <p className="text-sm text-slate-400 mb-1">Branch Name</p>
            <code className="text-blue-400 font-mono text-sm bg-slate-900/50 px-2 py-1 rounded">
              {preview.branch_name}
            </code>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">PR Title</p>
            <p className="text-white font-semibold">{preview.pr_title}</p>
          </div>
        </div>

        {/* Tabs for PR Body and Files */}
        <Tabs defaultValue="pr-body" className="space-y-4">
          <TabsList className="bg-slate-900/50 border border-slate-700">
            <TabsTrigger value="pr-body" className="data-[state=active]:bg-slate-800">
              PR Body
            </TabsTrigger>
            <TabsTrigger value="files" className="data-[state=active]:bg-slate-800">
              <FileText className="h-4 w-4 mr-2" />
              Files ({preview.files_to_create.length})
            </TabsTrigger>
          </TabsList>

          {/* PR Body Tab */}
          <TabsContent value="pr-body">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-white">Pull Request Body</CardTitle>
                  <Button
                    onClick={copyPRBody}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {copiedPRBody ? (
                      <>
                        <Check className="h-4 w-4 mr-2" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-2" />
                        Copy PR Body
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-slate-900/50 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-sm text-slate-300 whitespace-pre-wrap font-mono">
                    {preview.pr_body}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Files Tab */}
          <TabsContent value="files" className="space-y-4">
            {preview.files_to_create.map((file, index) => (
              <Card key={index} className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg text-white font-mono flex items-center gap-2">
                        <FileText className="h-5 w-5 text-blue-400" />
                        {file.path}
                      </CardTitle>
                      <CardDescription className="text-slate-400 mt-2">
                        {file.description}
                      </CardDescription>
                    </div>
                    <Button
                      onClick={() => copyFileContent(file.path, file.content)}
                      className="bg-slate-700 hover:bg-slate-600 text-white"
                    >
                      {copiedFile === file.path ? (
                        <>
                          <Check className="h-4 w-4 mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-slate-900/50 rounded-lg p-4 overflow-x-auto max-h-96">
                    <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono">
                      {file.content}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>

        {/* Info Badge */}
        <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
          <p className="text-sm text-blue-300">
            <strong>💡 Next Steps:</strong> Review the Shadow PR analysis above, download the complete package, 
            and use it to guide your implementation. The files can be added to your repository as documentation 
            before starting development.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// Made with Bob