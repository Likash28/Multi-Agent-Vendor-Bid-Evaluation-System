// Authentication Types
export interface User {
  id: string;
  email: string;
  name: string;
  department?: string;
  role?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  department?: string;
}

// Evaluation Types
export interface Evaluation {
  id: string;
  title: string;
  description?: string;
  status: EvaluationStatus;
  config: EvaluationConfig;
  results?: EvaluationResults;
  created_by: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  progress?: number;
}

export type EvaluationStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export interface EvaluationConfig {
  title: string;
  description?: string;
  rfp_document?: string;
  vendor_bids: VendorBid[];
  weights: EvaluationWeights;
  criteria: EvaluationCriteria;
  llm_config?: LLMConfig;
}

export interface VendorBid {
  vendor_id: string;
  vendor_name: string;
  documents: Document[];
}

export interface Document {
  id: string;
  name: string;
  type: string;
  url?: string;
  file_path?: string;
  size?: number;
  uploaded_at?: string;
}

export interface EvaluationWeights {
  technical: number;
  financial: number;
  compliance: number;
  experience?: number;
}

export interface EvaluationCriteria {
  technical?: string[];
  financial?: string[];
  compliance?: string[];
  experience?: string[];
}

export interface LLMConfig {
  model?: string;
  temperature?: number;
  max_tokens?: number;
  provider?: string;
}

// Evaluation Results Types
export interface EvaluationResults {
  evaluation_id: string;
  vendor_scores: VendorScore[];
  compliance_results?: ComplianceResult[];
  technical_results?: TechnicalResult[];
  financial_results?: FinancialResult[];
  summary?: EvaluationSummary;
  recommendations?: string[];
  created_at: string;
}

export interface VendorScore {
  vendor_id: string;
  vendor_name: string;
  total_score: number;
  weighted_score: number;
  scores: {
    technical: number;
    financial: number;
    compliance: number;
    experience?: number;
  };
  rank?: number;
  strengths?: string[];
  weaknesses?: string[];
  risk_assessment?: string;
}

export interface ComplianceResult {
  vendor_id: string;
  vendor_name: string;
  is_compliant: boolean;
  compliance_score: number;
  requirements_met: RequirementCheck[];
  missing_requirements: string[];
  non_compliant_items: string[];
  notes?: string;
}

export interface RequirementCheck {
  requirement: string;
  met: boolean;
  evidence?: string;
  notes?: string;
}

export interface TechnicalResult {
  vendor_id: string;
  vendor_name: string;
  technical_score: number;
  criteria_scores: CriteriaScore[];
  strengths: string[];
  weaknesses: string[];
  technical_capabilities: string[];
  innovation_score?: number;
  implementation_approach?: string;
}

export interface CriteriaScore {
  criteria: string;
  score: number;
  max_score: number;
  justification?: string;
}

export interface FinancialResult {
  vendor_id: string;
  vendor_name: string;
  financial_score: number;
  total_cost: number;
  cost_breakdown?: CostBreakdown;
  value_for_money_score?: number;
  pricing_structure?: string;
  payment_terms?: string;
  cost_analysis?: string;
}

export interface CostBreakdown {
  initial_cost?: number;
  recurring_cost?: number;
  implementation_cost?: number;
  maintenance_cost?: number;
  training_cost?: number;
  other_costs?: Record<string, number>;
}

export interface EvaluationSummary {
  total_vendors: number;
  evaluation_date: string;
  top_vendor: {
    vendor_id: string;
    vendor_name: string;
    score: number;
  };
  average_score: number;
  evaluation_criteria_used: string[];
  key_findings: string[];
  decision_factors: string[];
}

// Vendor Types
export interface Vendor {
  id: string;
  name: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  website?: string;
  description?: string;
  certifications?: string[];
  years_in_business?: number;
  created_at: string;
  updated_at: string;
}

// Bid Types
export interface Bid {
  id: string;
  evaluation_id: string;
  vendor_id: string;
  vendor_name: string;
  documents: Document[];
  submitted_at: string;
  status: "submitted" | "under_review" | "evaluated" | "rejected";
  notes?: string;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: "agent_update" | "progress" | "log" | "completion" | "error";
  data: unknown;
}

export interface AgentProgress {
  agent_name: string;
  status: "idle" | "processing" | "completed" | "failed";
  progress: number;
  message?: string;
  current_task?: string;
}

export interface ProcessingEvent {
  timestamp: string;
  level: "info" | "warning" | "error" | "success";
  message: string;
  agent?: string;
  details?: Record<string, unknown>;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status_code?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
