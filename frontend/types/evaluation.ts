export type EvaluationStatus = 'DRAFT' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export type EvaluationMethod = 'QCBS' | 'LCS' | 'FBS';

export type AgentType =
  | 'document_parser'
  | 'compliance_checker'
  | 'technical_evaluator'
  | 'financial_evaluator'
  | 'comparison_agent'
  | 'report_generator';

export type AgentStatus = 'pending' | 'running' | 'completed' | 'error';

export interface Evaluation {
  id: string;
  title: string;
  description?: string;
  status: EvaluationStatus;
  method: EvaluationMethod;
  technical_weight?: number;
  financial_weight?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  created_by: string;
  vendor_count?: number;
  winner_id?: string;
}

export interface AgentProgress {
  agent: AgentType;
  status: AgentStatus;
  progress: number;
  message: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface ProcessingEvent {
  timestamp: string;
  agent: AgentType;
  action: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
}

export interface VendorScore {
  vendor_id: string;
  vendor_name: string;
  compliance_status: 'PASS' | 'FAIL' | 'CONDITIONAL';
  compliance_score: number;
  technical_score: number;
  financial_score: number;
  total_score: number;
  rank: number;
  is_winner: boolean;
  submitted_at?: string;
}

export interface ComplianceResult {
  vendor_id: string;
  vendor_name: string;
  status: 'PASS' | 'FAIL' | 'CONDITIONAL';
  overall_score: number;
  documents: DocumentCheck[];
  issues: ComplianceIssue[];
  notes?: string;
}

export interface DocumentCheck {
  document_type: string;
  required: boolean;
  submitted: boolean;
  valid: boolean;
  notes?: string;
}

export interface ComplianceIssue {
  severity: 'critical' | 'major' | 'minor';
  description: string;
  document?: string;
}

export interface TechnicalScore {
  vendor_id: string;
  vendor_name: string;
  total_score: number;
  criteria: TechnicalCriterion[];
  overall_notes?: string;
}

export interface TechnicalCriterion {
  name: string;
  weight: number;
  score: number;
  weighted_score: number;
  justification: string;
}

export interface FinancialAnalysis {
  vendor_id: string;
  vendor_name: string;
  quoted_price: number;
  adjusted_price: number;
  price_score: number;
  rank: number;
  is_l1: boolean;
  adjustments?: PriceAdjustment[];
  notes?: string;
}

export interface PriceAdjustment {
  type: string;
  amount: number;
  reason: string;
}

export interface EvaluationResults {
  evaluation_id: string;
  status: EvaluationStatus;
  method: EvaluationMethod;
  rankings: VendorScore[];
  compliance: ComplianceResult[];
  technical: TechnicalScore[];
  financial: FinancialAnalysis[];
  processing_time?: number;
  completed_at?: string;
  report_url?: string;
}

export interface WebSocketMessage {
  type: 'agent_update' | 'progress' | 'log' | 'completion' | 'error';
  data: any;
}
