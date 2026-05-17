/**
 * Shadow PR Types
 * Complete Shadow PR contract matching backend schema
 */

export interface ShadowPRFile {
  path: string;
  content: string;
  description: string;
}

export interface ShadowPRPreview {
  analysis_id: string;
  branch_name: string;
  pr_title: string;
  pr_body: string;
  files_to_create: ShadowPRFile[];
  summary: string;
}

export interface ShadowPRDownloadPackage {
  preview: ShadowPRPreview;
  files: Array<{
    filename: string;
    content: string;
  }>;
  metadata: {
    generated_at: string;
    analysis_id: string;
    repository_name: string;
    change_description: string;
  };
}

// Made with Bob