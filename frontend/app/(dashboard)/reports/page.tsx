"use client"

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Report, ReportFormat } from '@/types/report';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getStatusColor, formatDateTime, formatDate } from '@/lib/utils';
import { Download, FileText, Search, Filter } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [formatFilter, setFormatFilter] = useState<ReportFormat | 'ALL'>('ALL');

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch('/api/reports');
        if (response.ok) {
          const data = await response.json();
          setReports(data);
        }
      } catch (error) {
        console.error('Failed to fetch reports:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReports();
  }, []);

  const filteredReports = reports.filter((report) => {
    const matchesSearch =
      report.evaluation_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFormat = formatFilter === 'ALL' || report.format === formatFilter;
    return matchesSearch && matchesFormat;
  });

  const handleDownload = async (report: Report) => {
    if (!report.file_url) return;

    try {
      const response = await fetch(report.file_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${report.id}.${report.format.toLowerCase()}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Reports</h1>
          <p className="text-muted-foreground">
            Generated evaluation reports and exports
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={formatFilter} onValueChange={(value) => setFormatFilter(value as ReportFormat | 'ALL')}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Formats</SelectItem>
              <SelectItem value="PDF">PDF</SelectItem>
              <SelectItem value="XLSX">Excel</SelectItem>
              <SelectItem value="DOCX">Word</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Reports"
          value={reports.length.toString()}
          icon={<FileText className="h-5 w-5" />}
        />
        <StatCard
          label="PDF"
          value={reports.filter((r) => r.format === 'PDF').length.toString()}
          icon={<FileText className="h-5 w-5" />}
        />
        <StatCard
          label="Excel"
          value={reports.filter((r) => r.format === 'XLSX').length.toString()}
          icon={<FileText className="h-5 w-5" />}
        />
        <StatCard
          label="Word"
          value={reports.filter((r) => r.format === 'DOCX').length.toString()}
          icon={<FileText className="h-5 w-5" />}
        />
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Evaluation</TableHead>
              <TableHead>Format</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Generated</TableHead>
              <TableHead>Generated By</TableHead>
              <TableHead className="w-32">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredReports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No reports found
                </TableCell>
              </TableRow>
            ) : (
              filteredReports.map((report) => (
                <TableRow key={report.id}>
                  <TableCell>
                    <Button
                      variant="link"
                      className="p-0 h-auto"
                      onClick={() => router.push(`/evaluations/${report.evaluation_id}`)}
                    >
                      {report.evaluation_title}
                    </Button>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{report.format}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(report.status)}>
                      {report.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {report.file_size
                      ? `${(report.file_size / 1024).toFixed(1)} KB`
                      : '-'}
                  </TableCell>
                  <TableCell>{formatDateTime(report.generated_at)}</TableCell>
                  <TableCell>{report.generated_by}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      {report.status === 'COMPLETED' && report.file_url && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownload(report)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
}

function StatCard({ label, value, icon }: StatCardProps) {
  return (
    <div className="border rounded-lg p-4 bg-card">
      <div className="flex items-center gap-2 mb-2 text-muted-foreground">
        {icon}
        <p className="text-sm">{label}</p>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div>
        <Skeleton className="h-8 w-48 mb-2" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-full max-w-sm" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
