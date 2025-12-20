export type VendorStatus = 'ACTIVE' | 'INACTIVE' | 'SUSPENDED' | 'BLACKLISTED';

export interface Vendor {
  id: string;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  registration_number?: string;
  tax_id?: string;
  status: VendorStatus;
  verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface VendorDetail extends Vendor {
  contact_person?: string;
  website?: string;
  description?: string;
  certifications?: string[];
  evaluation_history: VendorEvaluationHistory[];
}

export interface VendorEvaluationHistory {
  evaluation_id: string;
  evaluation_title: string;
  evaluation_date: string;
  rank: number;
  total_score: number;
  won: boolean;
  status: string;
}
