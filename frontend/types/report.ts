export type ReportFormat = 'PDF' | 'XLSX' | 'DOCX';

export type ReportStatus = 'GENERATING' | 'COMPLETED' | 'FAILED';

export interface Report {
  id: string;
  evaluation_id: string;
  evaluation_title: string;
  format: ReportFormat;
  status: ReportStatus;
  file_url?: string;
  file_size?: number;
  generated_at: string;
  generated_by: string;
}

export interface ReportContent {
  markdown: string;
  metadata: {
    evaluation_id: string;
    title: string;
    method: string;
    generated_at: string;
    winner: string;
  };
}
