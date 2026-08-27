import { describe, expect, it } from 'vitest';

import { dispatchCommand } from '@/app/commands/dispatcher';
import { useAppStore } from '@/store/appStore';
import { selectCurrentRoomId, selectIsTransitioning, selectLocale } from '@/store/selectors';
import { asProjectId } from '@/types/ids';

describe('application state selectors', () => {
  it('records language as a single source of truth', () => {
    dispatchCommand({ type: 'SET_LANGUAGE', locale: 'zh-CN', source: 'user' });
    expect(selectLocale(useAppStore.getState())).toBe('zh-CN');
  });

  it('does not duplicate selection when opening a project', () => {
    dispatchCommand({ type: 'OPEN_PROJECT', projectId: asProjectId('demo'), source: 'user' });
    const state = useAppStore.getState();
    expect(state.selection.projectId).toBe('demo');
    expect(state.selection.contactOpen).toBe(false);
  });

  it('marks navigation as transitioning until completion', () => {
    dispatchCommand({ type: 'NAVIGATE_TO_ROOM', roomId: 'projects', source: 'user' });
    const state = useAppStore.getState();
    expect(selectIsTransitioning(state)).toBe(true);
    expect(selectCurrentRoomId(state)).toBe('identity');
  });
});
