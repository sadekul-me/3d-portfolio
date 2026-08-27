import { describe, expect, it } from 'vitest';

import { createNavigationSnapshot, reduceNavigation } from '@/navigation/fsm/navigationFsm';

describe('navigation FSM', () => {
  it('moves IDLE → REQUESTED → TRANSITIONING → ARRIVED → ACTIVE', () => {
    const state = createNavigationSnapshot('identity');
    const requested = reduceNavigation(state, { type: 'REQUEST', target: 'engineering' });
    expect(requested.accepted).toBe(true);
    expect(requested.state.phase).toBe('REQUESTED');

    const transitioning = reduceNavigation(requested.state, { type: 'BEGIN_TRANSITION' });
    expect(transitioning.state.phase).toBe('TRANSITIONING');

    const arrived = reduceNavigation(transitioning.state, { type: 'ARRIVE' });
    expect(arrived.state.phase).toBe('ARRIVED');
    expect(arrived.state.currentRoomId).toBe('engineering');

    const active = reduceNavigation(arrived.state, { type: 'ACTIVATE' });
    expect(active.state.phase).toBe('ACTIVE');
    expect(active.state.targetRoomId).toBeNull();
  });

  it('ignores duplicate requests to the current room', () => {
    const state = createNavigationSnapshot('identity');
    const result = reduceNavigation(
      { ...state, phase: 'ACTIVE' },
      { type: 'REQUEST', target: 'identity' },
    );
    expect(result.accepted).toBe(false);
    expect(result.reason).toBe('ALREADY_AT_TARGET');
  });

  it('retargets instead of running two transitions', () => {
    const transitioning = reduceNavigation(
      { ...createNavigationSnapshot('identity'), phase: 'TRANSITIONING', targetRoomId: 'projects' },
      { type: 'REQUEST', target: 'ai-lab' },
    );
    expect(transitioning.accepted).toBe(true);
    expect(transitioning.state.phase).toBe('REQUESTED');
    expect(transitioning.state.targetRoomId).toBe('ai-lab');
    expect(transitioning.state.interrupted).toBe(true);
  });

  it('skips cinematic travel under reduced motion', () => {
    const result = reduceNavigation(createNavigationSnapshot('exterior'), {
      type: 'REQUEST',
      target: 'identity',
      reducedMotion: true,
    });
    expect(result.state.phase).toBe('ARRIVED');
    expect(result.state.currentRoomId).toBe('identity');
  });

  it('fails to a safe active state without leaving a corrupt phase', () => {
    const result = reduceNavigation(
      { ...createNavigationSnapshot('projects'), phase: 'TRANSITIONING', targetRoomId: 'ai-lab' },
      { type: 'FAIL' },
    );
    expect(result.state.phase).toBe('ACTIVE');
    expect(result.state.currentRoomId).toBe('projects');
  });
});
