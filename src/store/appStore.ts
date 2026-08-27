import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

import { createInitialAppState, type AppStoreState } from '@/store/types';

export type AppStore = AppStoreState & {
  replace: (next: AppStoreState) => void;
};

export const useAppStore = create<AppStore>()(
  subscribeWithSelector((set) => ({
    ...createInitialAppState(),
    replace: (next) => set(next),
  })),
);

export function getAppState(): AppStoreState {
  const { replace: _replace, ...state } = useAppStore.getState();
  return state;
}
