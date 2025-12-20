"use client"

import { ComplianceResult } from '@/types/evaluation';
import { Badge } from '@/components/ui/badge';
import { getStatusColor } from '@/lib/utils';
import { CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react';

interface ComplianceResultsProps {
  results: ComplianceResult[];
}

export function ComplianceResults({ results }: ComplianceResultsProps) {
  return (
    <div className="space-y-6">
      {results.map((result) => (
        <ComplianceCard key={result.vendor_id} result={result} />
      ))}
    </div>
  );
}

interface ComplianceCardProps {
  result: ComplianceResult;
}

function ComplianceCard({ result }: ComplianceCardProps) {
  const getStatusIcon = () => {
    switch (result.status) {
      case 'PASS':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'FAIL':
        return <XCircle className="h-6 w-6 text-red-600" />;
      default:
        return <AlertCircle className="h-6 w-6 text-yellow-600" />;
    }
  };

  return (
    <div className="border rounded-lg p-6 bg-card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold">{result.vendor_name}</h3>
            <p className="text-sm text-muted-foreground">
              Overall Score: {result.overall_score.toFixed(1)}%
            </p>
          </div>
        </div>
        <Badge className={getStatusColor(result.status)}>{result.status}</Badge>
      </div>

      {/* Document Checklist */}
      <div className="mb-4">
        <h4 className="font-semibold text-sm mb-3">Document Checklist</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {result.documents.map((doc, index) => (
            <DocumentCheckItem key={index} doc={doc} />
          ))}
        </div>
      </div>

      {/* Issues */}
      {result.issues.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold text-sm mb-3">Issues & Warnings</h4>
          <div className="space-y-2">
            {result.issues.map((issue, index) => (
              <IssueItem key={index} issue={issue} />
            ))}
          </div>
        </div>
      )}

      {/* AI Notes */}
      {result.notes && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-sm mb-2 text-blue-900">AI Analysis</h4>
          <p className="text-sm text-blue-800">{result.notes}</p>
        </div>
      )}
    </div>
  );
}

interface DocumentCheckItemProps {
  doc: {
    document_type: string;
    required: boolean;
    submitted: boolean;
    valid: boolean;
    notes?: string;
  };
}

function DocumentCheckItem({ doc }: DocumentCheckItemProps) {
  const getIcon = () => {
    if (!doc.submitted) {
      return <XCircle className="h-4 w-4 text-red-600" />;
    }
    if (!doc.valid) {
      return <AlertCircle className="h-4 w-4 text-yellow-600" />;
    }
    return <CheckCircle className="h-4 w-4 text-green-600" />;
  };

  return (
    <div className="flex items-start gap-2 p-2 border rounded">
      {getIcon()}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <FileText className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">{doc.document_type}</span>
          {doc.required && (
            <Badge variant="outline" className="text-xs">
              Required
            </Badge>
          )}
        </div>
        {doc.notes && (
          <p className="text-xs text-muted-foreground mt-1">{doc.notes}</p>
        )}
      </div>
    </div>
  );
}

interface IssueItemProps {
  issue: {
    severity: 'critical' | 'major' | 'minor';
    description: string;
    document?: string;
  };
}

function IssueItem({ issue }: IssueItemProps) {
  const getSeverityColor = () => {
    switch (issue.severity) {
      case 'critical':
        return 'border-red-500 bg-red-50';
      case 'major':
        return 'border-orange-500 bg-orange-50';
      default:
        return 'border-yellow-500 bg-yellow-50';
    }
  };

  const getSeverityBadge = () => {
    const colors = {
      critical: 'bg-red-600 text-white',
      major: 'bg-orange-600 text-white',
      minor: 'bg-yellow-600 text-white',
    };
    return (
      <Badge className={colors[issue.severity]}>
        {issue.severity.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className={`border-l-4 p-3 rounded ${getSeverityColor()}`}>
      <div className="flex items-start justify-between mb-1">
        {getSeverityBadge()}
        {issue.document && (
          <span className="text-xs text-muted-foreground">{issue.document}</span>
        )}
      </div>
      <p className="text-sm">{issue.description}</p>
    </div>
  );
}
