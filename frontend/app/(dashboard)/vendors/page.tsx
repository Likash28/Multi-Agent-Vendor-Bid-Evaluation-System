"use client"

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Vendor } from '@/types/vendor';
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
import { getStatusColor, formatDate } from '@/lib/utils';
import { Search, Plus, CheckCircle, XCircle } from 'lucide-react';

export default function VendorsPage() {
  const router = useRouter();
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchVendors = async () => {
      try {
        const response = await fetch('/api/vendors');
        if (response.ok) {
          const data = await response.json();
          setVendors(data);
        }
      } catch (error) {
        console.error('Failed to fetch vendors:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchVendors();
  }, []);

  const filteredVendors = vendors.filter(
    (vendor) =>
      vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vendor.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vendor.registration_number?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Vendors</h1>
          <p className="text-muted-foreground">
            Manage vendor information and verification status
          </p>
        </div>
        <Button onClick={() => router.push('/vendors/new')}>
          <Plus className="h-4 w-4 mr-2" />
          Add Vendor
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search vendors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Vendors"
          value={vendors.length.toString()}
          color="blue"
        />
        <StatCard
          label="Active"
          value={vendors.filter((v) => v.status === 'ACTIVE').length.toString()}
          color="green"
        />
        <StatCard
          label="Verified"
          value={vendors.filter((v) => v.verified).length.toString()}
          color="purple"
        />
        <StatCard
          label="Suspended"
          value={vendors.filter((v) => v.status === 'SUSPENDED').length.toString()}
          color="red"
        />
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Registration No.</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Verified</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredVendors.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No vendors found
                </TableCell>
              </TableRow>
            ) : (
              filteredVendors.map((vendor) => (
                <TableRow key={vendor.id}>
                  <TableCell className="font-medium">{vendor.name}</TableCell>
                  <TableCell>{vendor.email}</TableCell>
                  <TableCell>
                    <span className="font-mono text-sm">
                      {vendor.registration_number || '-'}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(vendor.status)}>
                      {vendor.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {vendor.verified ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                  </TableCell>
                  <TableCell>{formatDate(vendor.created_at)}</TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/vendors/${vendor.id}`)}
                    >
                      View
                    </Button>
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
  color: 'blue' | 'green' | 'purple' | 'red';
}

function StatCard({ label, value, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-900',
    green: 'bg-green-100 text-green-900',
    purple: 'bg-purple-100 text-purple-900',
    red: 'bg-red-100 text-red-900',
  };

  return (
    <div className="border rounded-lg p-4 bg-card">
      <p className="text-sm text-muted-foreground mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>
      <Skeleton className="h-10 w-full max-w-sm" />
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
