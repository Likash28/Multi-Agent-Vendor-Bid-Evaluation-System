import { AgentType } from '@/types/evaluation';

export const AGENT_LABELS: Record<AgentType, string> = {
  document_parser: 'Document Parser',
  compliance_checker: 'Compliance Checker',
  technical_evaluator: 'Technical Evaluator',
  financial_evaluator: 'Financial Evaluator',
  comparison_agent: 'Comparison Agent',
  report_generator: 'Report Generator',
};

export const AGENT_DESCRIPTIONS: Record<AgentType, string> = {
  document_parser: 'Parsing bid documents and extracting data',
  compliance_checker: 'Verifying compliance with requirements',
  technical_evaluator: 'Scoring technical proposals',
  financial_evaluator: 'Analyzing pricing and financial data',
  comparison_agent: 'Generating vendor rankings',
  report_generator: 'Creating final evaluation report',
};

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000';
