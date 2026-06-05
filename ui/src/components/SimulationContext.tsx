import { createContext, useState, useEffect, type ReactNode } from 'react';
import { usePopUp } from '../hooks/usePopUp';
import { type SimulationContextType } from '../types/simulation';

export const SimulationContext = createContext<SimulationContextType | null>(null);

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [simulationRunning, setSimulationRunning] = useState(
    () => localStorage.getItem('simulationRunning') === 'true'
  );
  const { popUps, addPopUp, removePopUp } = usePopUp();

  useEffect(() => {
    if (!simulationRunning) return;

    const events = new EventSource('http://localhost:8000/initiate/stream');

    events.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.status === 'completed') {
        setSimulationRunning(false);
        localStorage.removeItem('simulationRunning');
        addPopUp({ type: 'success', message: 'Simulation completed!' });
        events.close();
      }

      if (data.status === 'failed') {
        setSimulationRunning(false);
        localStorage.removeItem('simulationRunning');
        addPopUp({ type: 'error', message: 'Simulation failed.', description: data.error });
        events.close();
      }
    };

    events.onerror = () => {
      setSimulationRunning(false);
      localStorage.removeItem('simulationRunning');
      addPopUp({ type: 'error', message: 'Lost connection to simulation.' });
      events.close();
    };

    return () => events.close();
  }, [simulationRunning, addPopUp]);

  return (
    <SimulationContext.Provider value={{ simulationRunning, setSimulationRunning, popUps, addPopUp, removePopUp }}>
      {children}
    </SimulationContext.Provider>
  );
}