import { type FC } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import FormInput from './shared/FormInput';
import Button from './shared/Button';
import LLMSetup from './shared/LLMSetup';
import { type HelperAgentConfig } from '../types/agentConfigs';


interface HelperAgentConfigCardProps {
    predefined?: boolean;
    agent: HelperAgentConfig;
    onChange: (agent: HelperAgentConfig) => void;
    onNext: () => void;
    onBack: () => void;
}

const HelperAgentConfigCard: FC<HelperAgentConfigCardProps> = ({ predefined, agent, onChange, onNext, onBack }) => {
    const isValid = agent.name.trim() !== '';

    return (
        <div className="p-6 max-w-3xl mx-auto space-y-6 pb-24">
            <div className="flex items-start justify-between">
                <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-1">Analyst Agent Configuration</h4>
                    <p className="text-sm text-gray-500">The analyst agent extracts and validates requirements and issues after each stakeholder turn.</p>
                </div>
            </div>

            {predefined ? (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-700">
                        You are using a predefined scenario. The analyst agent configuration has been set automatically.
                    </p>
                </div>
            ) : (
                <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-md bg-purple-50 flex items-center justify-center text-sm">🔍</div>
                            <span className="text-sm font-semibold text-gray-900">Analyst Agent</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 border-t border-gray-200 bg-white px-6 py-4">
                        <FormInput
                            label="Agent Name"
                            value={agent.name}
                            onChange={(e) => onChange({ ...agent, name: e.target.value })}
                        />
                    </div>

                    <LLMSetup
                        config={agent}
                        onChange={cfg => onChange({ ...agent, ...cfg })}
                    />
                </div>
            )}

            <div className="flex justify-end pt-2 space-x-2 border-t border-gray-200">
                <Button variant="outline" onClick={onBack}>
                    <span className="flex items-center gap-2 cursor-pointer">
                        <ChevronLeft size={16} />
                        Back
                    </span>
                </Button>
                <Button onClick={onNext} disabled={!predefined && !isValid}>
                    <span className="flex items-center gap-2 cursor-pointer">
                        Continue
                        <ChevronRight size={16} />
                    </span>
                </Button>
            </div>
        </div>
    );
};

export default HelperAgentConfigCard;