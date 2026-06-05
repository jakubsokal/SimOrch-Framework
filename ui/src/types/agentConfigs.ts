import { type Provider } from '../components/shared/LLMSetup';

export interface HelperAgentConfig {
  name: string;
  role: number;
  provider: Provider;
  model: string;
  params: {
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  context_prompt: string;
  api_key?: string;
}

export const DEFAULT_HELPER_AGENT: HelperAgentConfig = {
  name: 'Analyst Agent',
  role: 3,
  provider: 'openai',
  model: 'gpt-4o-mini',
  params: {
    temperature: 0.0,
    top_p: 1.0,
    max_tokens: 512,
  },
  context_prompt: '',
  api_key: '',
};

export interface REAgentConfig {
  name: string;
  role?: number; // 1 for RE Agent, 2 for User Agent
  persona: {
    experience_level: string;
    questioning_strategy: string;
    probing_intensity: string;
    requirement_focus: string;
    tone: string;
    output_prefixes: string[];
  },
  provider: Provider;
  model: string;
  params: {
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  context_prompt: string;
  api_key?: string;
}

export const DEFAULT_RE_AGENT: REAgentConfig = {
  name: '',
  role: 1,
  persona: {
    experience_level: '',
    questioning_strategy: '',
    probing_intensity: '',
    requirement_focus: '',
    tone: '',
    output_prefixes: ['FR', 'NFR', 'CON'],
  },
  provider: 'ollama',
  model: 'llama2',
  params: {
    temperature: 0.0,
    top_p: 1.0,
    max_tokens: 512
  },
  context_prompt: '',
  api_key: '',
};

export interface UserAgentConfig {
    name: string;
    role?: number; // 1 for RE Agent, 2 for User Agent
    persona: { 
        communication_style: string;
        domain_knowledge_level: string;
        clarity_level: string;
        revelation_strategy: string;
        revelation_rate: string;
    },
    provider: Provider;
    model: string;
    params: {
        temperature: number;
        top_p: number;
        max_tokens: number;
    };
    context_prompt: string;
    api_key?: string;
}


export const DEFAULT_USER_AGENT: UserAgentConfig = {
    name: '',
    role: 2,
    persona: {
        communication_style: '',
        domain_knowledge_level: '',
        clarity_level: '',
        revelation_strategy: '',
        revelation_rate: '',
    },
    provider: 'ollama',
    model: 'llama2',
    params: {
        temperature: 0.0,
        top_p: 1.0,
        max_tokens: 512,
    },
    context_prompt: '',
    api_key: '',
};