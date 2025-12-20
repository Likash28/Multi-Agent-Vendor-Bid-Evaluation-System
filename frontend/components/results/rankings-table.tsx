"use client"

import { useState } from 'react';
import { VendorScore } from '@/types/evaluation';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getStatusColor } from '@/lib/utils';
import { ChevronDown, ChevronUp, Trophy } from 'lucide-react';

interface RankingsTableProps {
  rankings: VendorScore[];
}

export function RankingsTable({ rankings }: RankingsTableProps) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof VendorScore;
    direction: 'asc' | 'desc';
  }>({ key: 'rank', direction: 'asc' });

  const handleSort = (key: keyof VendorScore) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc',
    });
  };

  const sortedRankings = [...rankings].sort((a, b) => {
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
    }

    return 0;
  });

  return (
    <div className="border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Rank</TableHead>
            <TableHead>Vendor</TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleSort('compliance_score')}
              >
                Compliance
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleSort('technical_score')}
              >
                Technical
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleSort('financial_score')}
              >
                Financial
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleSort('total_score')}
              >
                Total Score
              </Button>
            </TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-16"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedRankings.map((vendor) => (
            <>
              <TableRow
                key={vendor.vendor_id}
                className={vendor.is_winner ? 'bg-yellow-50 font-semibold' : ''}
              >
                <TableCell>
                  <div className="flex items-center gap-2">
                    {vendor.is_winner && <Trophy className="h-4 w-4 text-yellow-500" />}
                    #{vendor.rank}
                  </div>
                </TableCell>
                <TableCell>{vendor.vendor_name}</TableCell>
                <TableCell>
                  <span className="font-medium">
                    {vendor.compliance_score.toFixed(1)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="font-medium">
                    {vendor.technical_score.toFixed(1)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="font-medium">
                    {vendor.financial_score.toFixed(1)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-lg font-bold">
                    {vendor.total_score.toFixed(1)}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge className={getStatusColor(vendor.compliance_status)}>
                    {vendor.compliance_status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      setExpandedRow(
                        expandedRow === vendor.vendor_id ? null : vendor.vendor_id
                      )
                    }
                  >
                    {expandedRow === vendor.vendor_id ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </TableCell>
              </TableRow>
              {expandedRow === vendor.vendor_id && (
                <TableRow>
                  <TableCell colSpan={8} className="bg-muted/50">
                    <div className="p-4 space-y-2">
                      <h4 className="font-semibold">Details</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Vendor ID</p>
                          <p className="font-mono">{vendor.vendor_id}</p>
                        </div>
                        {vendor.submitted_at && (
                          <div>
                            <p className="text-muted-foreground">Submitted At</p>
                            <p>{new Date(vendor.submitted_at).toLocaleString()}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
