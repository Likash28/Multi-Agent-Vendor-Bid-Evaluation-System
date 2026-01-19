/**
 * Vendor API Service
 * Handles vendor-related API calls
 */

import api from "./api";

export interface Vendor {
  id: string;
  name: string;
  registration_no?: string;
  gstin?: string;
  contact_email?: string;
  contact_phone?: string;
  is_verified: boolean;
  created_at: string;
}

export interface VendorListResponse {
  items: Vendor[];
  total: number;
  page: number;
  pages: number;
}

/**
 * Search for existing vendors
 */
export async function searchVendors(
  search?: string,
  verified?: boolean,
  page: number = 1,
  limit: number = 20
): Promise<VendorListResponse> {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (verified !== undefined) params.append("verified", String(verified));
  params.append("page", String(page));
  params.append("limit", String(limit));

  const response = await api.get<VendorListResponse>(
    `/vendors?${params.toString()}`
  );
  return response.data;
}

/**
 * Get vendor by ID
 */
export async function getVendor(vendorId: string): Promise<Vendor> {
  const response = await api.get<Vendor>(`/vendors/${vendorId}`);
  return response.data;
}

/**
 * Create or get vendor (get_or_create pattern)
 * This will return existing vendor if found by GSTIN/name, or create a new one
 */
export async function createOrGetVendor(data: {
  name: string;
  gstin?: string;
  registration_no?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
}): Promise<Vendor> {
  const response = await api.post<Vendor>("/vendors", data);
  return response.data;
}

