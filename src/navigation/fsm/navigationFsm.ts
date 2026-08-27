import type { RoomId } from '@/types/ids';
import { FALLBACK_ROOM_ID } from '@/navigation/graph/resolvePath';

export const NAVIGATION_PHASES = [
  'IDLE',
  'REQUESTED',
  'TRANSITIONING',
  'ARRIVED',
  'ACTIVE',
] as const;
export type NavigationPhase = (typeof NAVIGATION_PHASES)[number];

export type NavigationSnapshot = {
  phase: NavigationPhase;
  currentRoomId: RoomId;
  targetRoomId: RoomId | null;
  visitedRoomIds: readonly RoomId[];
  interrupted: boolean;
};

export type NavigationFsmEvent =
  | { type: 'REQUEST'; target: RoomId; reducedMotion?: boolean }
  | { type: 'BEGIN_TRANSITION' }
  | { type: 'ARRIVE' }
  | { type: 'ACTIVATE' }
  | { type: 'INTERRUPT'; target: RoomId }
  | { type: 'FAIL' }
  | { type: 'RESET' };

export type NavigationFsmResult = {
  state: NavigationSnapshot;
  accepted: boolean;
  reason?: string;
};

export function createNavigationSnapshot(
  currentRoomId: RoomId = FALLBACK_ROOM_ID,
): NavigationSnapshot {
  return {
    phase: 'IDLE',
    currentRoomId,
    targetRoomId: null,
    visitedRoomIds: [currentRoomId],
    interrupted: false,
  };
}

function withVisit(state: NavigationSnapshot, roomId: RoomId): readonly RoomId[] {
  if (state.visitedRoomIds.includes(roomId)) {
    return state.visitedRoomIds;
  }
  return [...state.visitedRoomIds, roomId];
}

/**
 * Pure navigation lifecycle. Camera/GSAP systems observe phase changes;
 * they never own the source of truth.
 */
export function reduceNavigation(
  state: NavigationSnapshot,
  event: NavigationFsmEvent,
): NavigationFsmResult {
  switch (event.type) {
    case 'REQUEST': {
      if (
        event.target === state.currentRoomId &&
        (state.phase === 'IDLE' || state.phase === 'ACTIVE')
      ) {
        return { state, accepted: false, reason: 'ALREADY_AT_TARGET' };
      }
      if (state.phase === 'TRANSITIONING') {
        return {
          state: {
            ...state,
            interrupted: true,
            targetRoomId: event.target,
            phase: 'REQUESTED',
          },
          accepted: true,
          reason: 'INTERRUPTED_AND_RETARGETED',
        };
      }
      if (state.phase === 'REQUESTED' && state.targetRoomId === event.target) {
        return { state, accepted: false, reason: 'DUPLICATE_REQUEST' };
      }
      return {
        state: {
          ...state,
          phase: event.reducedMotion ? 'ARRIVED' : 'REQUESTED',
          targetRoomId: event.target,
          currentRoomId: event.reducedMotion ? event.target : state.currentRoomId,
          visitedRoomIds: event.reducedMotion
            ? withVisit(state, event.target)
            : state.visitedRoomIds,
          interrupted: false,
        },
        accepted: true,
      };
    }
    case 'BEGIN_TRANSITION': {
      if (state.phase !== 'REQUESTED' || !state.targetRoomId) {
        return { state, accepted: false, reason: 'INVALID_TRANSITION' };
      }
      return {
        state: { ...state, phase: 'TRANSITIONING' },
        accepted: true,
      };
    }
    case 'ARRIVE': {
      if ((state.phase !== 'TRANSITIONING' && state.phase !== 'REQUESTED') || !state.targetRoomId) {
        return { state, accepted: false, reason: 'INVALID_ARRIVAL' };
      }
      return {
        state: {
          ...state,
          phase: 'ARRIVED',
          currentRoomId: state.targetRoomId,
          visitedRoomIds: withVisit(state, state.targetRoomId),
          interrupted: false,
        },
        accepted: true,
      };
    }
    case 'ACTIVATE': {
      if (state.phase !== 'ARRIVED') {
        return { state, accepted: false, reason: 'INVALID_ACTIVATE' };
      }
      return {
        state: {
          ...state,
          phase: 'ACTIVE',
          targetRoomId: null,
        },
        accepted: true,
      };
    }
    case 'INTERRUPT': {
      if (state.phase !== 'TRANSITIONING' && state.phase !== 'REQUESTED') {
        return { state, accepted: false, reason: 'NOTHING_TO_INTERRUPT' };
      }
      return {
        state: {
          ...state,
          phase: 'REQUESTED',
          targetRoomId: event.target,
          interrupted: true,
        },
        accepted: true,
      };
    }
    case 'FAIL': {
      return {
        state: {
          ...createNavigationSnapshot(state.currentRoomId),
          visitedRoomIds: state.visitedRoomIds,
          phase: 'ACTIVE',
        },
        accepted: true,
        reason: 'SAFE_RESET',
      };
    }
    case 'RESET': {
      return {
        state: createNavigationSnapshot(FALLBACK_ROOM_ID),
        accepted: true,
      };
    }
    default: {
      return { state, accepted: false, reason: 'UNKNOWN_EVENT' };
    }
  }
}
