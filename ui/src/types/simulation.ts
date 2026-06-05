import type { PopUpItem } from "../components/shared/PopUp";

export type AgentRole = 1 | 2 | 3;

export type IssueType =
  | 'conflict'
  | 'process_gap'
  | 'ambiguity'
  | 'missing_requirement'
  | 'contradiction';

export type IssueSeverity = 'low' | 'medium' | 'high';

export type IssueStatus = 'open' | 'resolved' | 'wont_fix';

export interface IssueDetail {
  type: IssueType;
  description: string;
  severity: IssueSeverity;
  status: IssueStatus;
  related_requirement_id: number | null;
  evidence_quote: string;
  suggested_action?: string;
  affects_requirements?: string[]; 
}

export interface Issue {
  issue_id: number;
  trace_message_id: number;
  createdBy: string;
  turn_id: number;
  timestamp: string;
  issue: IssueDetail;
}

export interface Message {
  turn: number;
  id: number;
  agent: string;
  role: AgentRole;
  message: string;
  timestamp: string;
}

export type RequirementType = 'functional' | 'non-functional';

export interface RequirementDetail {
  type: RequirementType;
  description: string;
  needs_clarification: boolean;
  evidence_quote: string;
}

export interface Requirement {
  req_id: number;
  turn_id: number;
  createdBy: string;
  trace_message_id: number;
  timestamp: string;
  requirement: RequirementDetail;
}

export interface CustomScenarioData {
  scenario: {
    id: string;
    scenario_name: string;
    seed: number;
    description: string;
    domain: string;
    system_type: string;
    max_turns: number;
    conversation_type: string;
  };
}

export const DEFAULT_CUSTOM_SCENARIO: CustomScenarioData = {
  scenario: {
    id: '',
    scenario_name: '',
    seed: 0,
    description: '',
    domain: '',
    system_type: '',
    max_turns: 0,
    conversation_type: '',
  },
};

export interface SimulationContextType {
  simulationRunning: boolean;
  setSimulationRunning: (running: boolean) => void;
  popUps: PopUpItem[];
  addPopUp: (popUp: Omit<PopUpItem, 'id'>) => void;
  removePopUp: () => void;
}
  