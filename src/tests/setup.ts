import '@testing-library/jest-dom/vitest';

import { beforeEach } from 'vitest';

import { eventBus } from '@/events/bus/eventBus';
import { useAppStore } from '@/store/appStore';
import { createInitialAppState } from '@/store/types';
import { clearEventHistory } from '@/events/debug/eventHistory';

beforeEach(() => {
  useAppStore.getState().replace(createInitialAppState());
  eventBus.clear();
  clearEventHistory();
});
