"use client"

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { VendorDetail } from '@/types/vendor';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { getStatusColor, formatDate } from '@/lib/utils';
import {
  AlertCircle,
  Edit,
  Mail,
  Phone,
  MapPin,
  FileText,
  CheckCircle,
  XCircle,
  Trophy,
  Building,
  Globe,
} from 'lucide-react';

interface VendorDetailPageProps {
  params: {
    id: string;
  };
}

export default function VendorDetailPage({ params }: VendorDetailPageProps) {
  const router = useRouter();
  const [vendor, setVendor] = useState<VendorDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVendor = async () => {
      try {
        const response = await fetch(`/api/vendors/${params.id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch vendor details');
        }
        const data = await response.json();
        setVendor(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchVendor();
  }, [params.id]);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error || !vendor) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="border border-red-200 rounded-lg p-6 bg-red-50">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-8 w-8 text-red-600" />
            <div>
              <h2 className="text-xl font-semibold text-red-900">Error</h2>
              <p className="text-sm text-red-700">{error || 'Vendor not found'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold">{vendor.name}</h1>
            {vendor.verified && <CheckCircle className="h-6 w-6 text-green-600" />}
          </div>
          {vendor.description && (
            <p className="text-muted-foreground">{vendor.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getStatusColor(vendor.status)}>{vendor.status}</Badge>
          <Button variant="outline" onClick={() => router.push(`/vendors/${params.id}/edit`)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </div>
      </div>

      {/* Contact Information */}
      <div className="border rounded-lg p-6 bg-card">
        <h2 className="text-lg font-semibold mb-4">Contact Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {vendor.email && (
            <ContactItem icon={<Mail className="h-4 w-4" />} label="Email" value={vendor.email} />
          )}
          {vendor.phone && (
            <ContactItem icon={<Phone className="h-4 w-4" />} label="Phone" value={vendor.phone} />
          )}
          {vendor.address && (
            <ContactItem icon={<MapPin className="h-4 w-4" />} label="Address" value={vendor.address} />
          )}
          {vendor.contact_person && (
            <ContactItem icon={<Building className="h-4 w-4" />} label="Contact Person" value={vendor.contact_person} />
          )}
          {vendor.website && (
            <ContactItem icon={<Globe className="h-4 w-4" />} label="Website" value={vendor.website} />
          )}
          {vendor.registration_number && (
            <ContactItem icon={<FileText className="h-4 w-4" />} label="Registration No." value={vendor.registration_number} />
          )}
          {vendor.tax_id && (
            <ContactItem icon={<FileText className="h-4 w-4" />} label="Tax ID" value={vendor.tax_id} />
          )}
        </div>
      </div>

      {/* Certifications */}
      {vendor.certifications && vendor.certifications.length > 0 && (
        <div className="border rounded-lg p-6 bg-card">
          <h2 className="text-lg font-semibold mb-4">Certifications</h2>
          <div className="flex flex-wrap gap-2">
            {vendor.certifications.map((cert, index) => (
              <Badge key={index} variant="secondary">
                {cert}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Evaluation History */}
      <div className="border rounded-lg p-6 bg-card">
        <h2 className="text-lg font-semibold mb-4">Evaluation History</h2>
        {vendor.evaluation_history.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            No evaluation history available
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Evaluation</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Rank</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Result</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vendor.evaluation_history.map((history) => (
                <TableRow key={history.evaluation_id}>
                  <TableCell>
                    <Button
                      variant="link"
                      className="p-0 h-auto"
                      onClick={() => router.push(`/evaluations/${history.evaluation_id}`)}
                    >
                      {history.evaluation_title}
                    </Button>
                  </TableCell>
                  <TableCell>{formatDate(history.evaluation_date)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {history.won && <Trophy className="h-4 w-4 text-yellow-500" />}
                      #{history.rank}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge>{history.total_score.toFixed(1)}</Badge>
                  </TableCell>
                  <TableCell>
                    {history.won ? (
                      <Badge className="bg-green-600 text-white">Winner</Badge>
                    ) : (
                      <Badge variant="outline">Participant</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(history.status)}>
                      {history.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border rounded-lg p-4 bg-card">
          <p className="text-sm text-muted-foreground mb-1">Created At</p>
          <p className="font-semibold">{formatDate(vendor.created_at)}</p>
        </div>
        <div className="border rounded-lg p-4 bg-card">
          <p className="text-sm text-muted-foreground mb-1">Last Updated</p>
          <p className="font-semibold">{formatDate(vendor.updated_at)}</p>
        </div>
      </div>
    </div>
  );
}

interface ContactItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function ContactItem({ icon, label, value }: ContactItemProps) {
  return (
    <div className="flex items-start gap-3">
      <div className="p-2 bg-muted rounded-lg text-muted-foreground mt-0.5">
        {icon}
      </div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="font-medium">{value}</p>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <Skeleton className="h-10 w-64 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <Skeleton className="h-10 w-24" />
      </div>
      <Skeleton className="h-64 w-full" />
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
