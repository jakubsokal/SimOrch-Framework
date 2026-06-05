export const AgentType = {
  REQUIREMENTS_ENGINEER: 1,
  STAKEHOLDER: 2,
  HELPER_AGENT: 3,
} as const;

export type AgentType = typeof AgentType[keyof typeof AgentType];

export const AgentTypeLabels: Record<AgentType, string> = {
  [AgentType.REQUIREMENTS_ENGINEER]: 'Requirements Engineer',
  [AgentType.STAKEHOLDER]: 'Stakeholder',
  [AgentType.HELPER_AGENT]: 'Analyst Agent',
};