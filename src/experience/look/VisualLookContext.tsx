import { createContext, useContext } from 'react';

import type { VisualLook } from '@/experience/look/visualLook';

export type VisualLookContextValue = {
  look: VisualLook;
  setLook: (look: VisualLook) => void;
};

export const VisualLookContext = createContext<VisualLookContextValue | null>(null);

export function useVisualLook(): VisualLookContextValue {
  const value = useContext(VisualLookContext);
  if (!value) {
    return { look: 'SYSTEM', setLook: () => undefined };
  }
  return value;
}
