import { useContext } from 'react';
import { SimulationContext } from '../components/SimulationContext';
import { type SimulationContextType } from '../types/simulation';

export function useSimulation(): SimulationContextType {
  const context = useContext(SimulationContext);
  if (!context) throw new Error('useSimulation must be used within SimulationProvider');
  return context;
}