/**
 * Evaluation API Service
 * Handles all evaluation-related API calls
 */

import api from "./api";

export interface DocumentUploadResponse {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  mime_type: string;
  created_at: string;
}

export interface EvaluationCreateRequest {
  tender_document_id?: string;
  title: string;
  config?: {
    method: "l1" | "qcbs" | "two_stage";
    technical_weight: number;
    financial_weight: number;
    qualification_threshold: number;
    enable_compliance_check: boolean;
    enable_justifications: boolean;
    enable_cartel_detection: boolean;
  };
}

export interface EvaluationResponse {
  id: string;
  reference_id: string;
  title: string;
  status: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface BidAddRequest {
  vendor_id: string;
  document_id?: string;
}

/**
 * Upload a document (tender or bid)
 */
export async function uploadDocument(
  file: File,
  fileType: "tender" | "bid",
  metadata?: Record<string, any>
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("file_type", fileType);
  if (metadata) {
    formData.append("metadata", JSON.stringify(metadata));
  }

  const response = await api.post<DocumentUploadResponse>(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

/**
 * Create a new evaluation
 */
export async function createEvaluation(
  data: EvaluationCreateRequest
): Promise<EvaluationResponse> {
  const response = await api.post<EvaluationResponse>("/evaluations", data);
  return response.data;
}

/**
 * Add bids to an evaluation
 */
export async function addBidsToEvaluation(
  evaluationId: string,
  bids: BidAddRequest[]
): Promise<{ added: number }> {
  const response = await api.post<{ added: number }>(
    `/evaluations/${evaluationId}/bids`,
    bids
  );
  return response.data;
}

/**
 * Update evaluation configuration
 */
export async function updateEvaluationConfig(
  evaluationId: string,
  config: EvaluationCreateRequest["config"]
): Promise<EvaluationResponse> {
  const response = await api.patch<EvaluationResponse>(
    `/evaluations/${evaluationId}/config`,
    { ...config }
  );
  return response.data;
}

/**
 * Start the evaluation process
 */
export async function startEvaluation(
  evaluationId: string
): Promise<{
  id: string;
  status: string;
  estimated_time_seconds: number;
}> {
  const response = await api.post<{
    id: string;
    status: string;
    estimated_time_seconds: number;
  }>(`/evaluations/${evaluationId}/start`);
  return response.data;
}

