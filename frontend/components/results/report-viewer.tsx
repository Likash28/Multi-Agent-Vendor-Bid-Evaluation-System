"use client"

import { useState } from 'react';
import { ReportContent } from '@/types/report';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Download, Printer } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ReportViewerProps {
  report: ReportContent;
  evaluationId: string;
}

export function ReportViewer({ report, evaluationId }: ReportViewerProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownloadPdf = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(`/api/evaluations/${evaluationId}/report/pdf`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `evaluation-report-${evaluationId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PDF:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-4">
      {/* Actions */}
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h3 className="text-lg font-semibold">Evaluation Report</h3>
          <p className="text-sm text-muted-foreground">
            Generated on {new Date(report.metadata.generated_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handlePrint}>
            <Printer className="h-4 w-4 mr-2" />
            Print
          </Button>
          <Button onClick={handleDownloadPdf} disabled={isDownloading}>
            <Download className="h-4 w-4 mr-2" />
            {isDownloading ? 'Downloading...' : 'Download PDF'}
          </Button>
        </div>
      </div>

      {/* Report Content */}
      <ScrollArea className="h-[600px] border rounded-lg">
        <div className="p-8 max-w-4xl mx-auto prose prose-sm">
          <ReactMarkdown>{report.markdown}</ReactMarkdown>
        </div>
      </ScrollArea>
    </div>
  );
}
