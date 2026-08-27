import type { AppCommand } from '@/app/commands/types';
import type { DomainEvent } from '@/events/types/eventTypes';
import type { AppStoreState } from '@/store/types';
import { createCorrelationId } from '@/lib/ids';
import { eventBus } from '@/events/bus/eventBus';
import { useAppStore } from '@/store/appStore';
import { reduceNavigation } from '@/navigation/fsm/navigationFsm';
import { resolveDestination } from '@/navigation/graph/resolvePath';
import { STORAGE_KEYS, writeStorage } from '@/lib/storage';
import { isRoomId } from '@/types/ids';

export type CommandResult = {
  accepted: boolean;
  reason?: string;
};

function nowIso(): string {
  return new Date().toISOString();
}

function publish(event: DomainEvent): void {
  eventBus.publish(event);
}

function apply(mutator: (state: AppStoreState) => AppStoreState): AppStoreState {
  const current = useAppStore.getState();
  const snapshot: AppStoreState = {
    navigation: current.navigation,
    preferences: current.preferences,
    selection: current.selection,
    session: current.session,
  };
  const next = mutator(snapshot);
  current.replace(next);
  return next;
}

/**
 * Commands request change. State records truth. Events announce facts.
 * This is the only application-level mutation boundary for store-backed concerns.
 */
export function dispatchCommand(command: AppCommand): CommandResult {
  const correlationId = createCorrelationId(command.type.toLowerCase());

  switch (command.type) {
    case 'NAVIGATE_TO_ROOM': {
      const target = resolveDestination(command.roomId);
      if (!target || !isRoomId(command.roomId)) {
        publish({
          type: 'NAVIGATION_REJECTED',
          payload: { target: command.roomId, reason: 'UNKNOWN_ROOM' },
          correlationId,
          occurredAt: nowIso(),
        });
        return { accepted: false, reason: 'UNKNOWN_ROOM' };
      }

      const state = useAppStore.getState();
      const reducedMotion = state.preferences.reducedMotion || command.source === 'system';
      const result = reduceNavigation(state.navigation, {
        type: 'REQUEST',
        target,
        reducedMotion,
      });

      if (!result.accepted) {
        publish({
          type: 'NAVIGATION_REJECTED',
          payload: { target, reason: result.reason ?? 'REJECTED' },
          correlationId,
          occurredAt: nowIso(),
        });
        return { accepted: false, reason: result.reason ?? 'REJECTED' };
      }

      apply((current) => ({
        ...current,
        navigation: result.state,
        session: { ...current.session, currentRoomId: result.state.currentRoomId },
      }));

      if (result.reason === 'INTERRUPTED_AND_RETARGETED') {
        publish({
          type: 'NAVIGATION_INTERRUPTED',
          payload: { from: state.navigation.currentRoomId, to: target },
          correlationId,
          occurredAt: nowIso(),
        });
      }

      if (result.state.phase === 'ARRIVED' || result.state.phase === 'ACTIVE') {
        publish({
          type: 'ROOM_ENTERED',
          payload: { roomId: result.state.currentRoomId },
          correlationId,
          occurredAt: nowIso(),
        });
      }

      return { accepted: true };
    }
    case 'OPEN_PROJECT': {
      apply((current) => ({
        ...current,
        selection: {
          ...current.selection,
          projectId: command.projectId,
          resumeOpen: false,
          contactOpen: false,
        },
      }));
      publish({
        type: 'PROJECT_OPENED',
        payload: { projectId: command.projectId },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'CLOSE_PROJECT': {
      const currentId = useAppStore.getState().selection.projectId;
      apply((current) => ({
        ...current,
        selection: { ...current.selection, projectId: null },
      }));
      if (currentId) {
        publish({
          type: 'PROJECT_CLOSED',
          payload: { projectId: currentId },
          correlationId,
          occurredAt: nowIso(),
        });
      }
      return { accepted: true };
    }
    case 'SHOW_SKILL': {
      apply((current) => ({
        ...current,
        selection: { ...current.selection, skillId: command.skillId },
      }));
      publish({
        type: 'SKILL_SHOWN',
        payload: { skillId: command.skillId },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'SHOW_ARCHITECTURE': {
      apply((current) => ({
        ...current,
        selection: { ...current.selection, architectureCaseId: command.architectureCaseId },
      }));
      publish({
        type: 'ARCHITECTURE_SHOWN',
        payload: { architectureCaseId: command.architectureCaseId },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'SET_LANGUAGE': {
      writeStorage(STORAGE_KEYS.locale, command.locale);
      apply((current) => ({
        ...current,
        preferences: { ...current.preferences, locale: command.locale },
        session: { ...current.session, language: command.locale },
      }));
      publish({
        type: 'LANGUAGE_CHANGED',
        payload: { locale: command.locale },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'SET_QUALITY': {
      writeStorage(STORAGE_KEYS.qualityPreset, command.preset);
      apply((current) => ({
        ...current,
        preferences: { ...current.preferences, qualityPreset: command.preset },
      }));
      publish({
        type: 'QUALITY_CHANGED',
        payload: { preset: command.preset },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'SET_SOUND': {
      writeStorage(STORAGE_KEYS.soundEnabled, String(command.enabled));
      apply((current) => ({
        ...current,
        preferences: { ...current.preferences, soundEnabled: command.enabled },
      }));
      publish({
        type: 'SOUND_CHANGED',
        payload: { enabled: command.enabled },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'SET_EXPERIENCE_MODE': {
      writeStorage(STORAGE_KEYS.experienceModeOverride, command.mode);
      apply((current) => ({
        ...current,
        preferences: { ...current.preferences, experienceModeOverride: command.mode },
      }));
      publish({
        type: 'EXPERIENCE_MODE_CHANGED',
        payload: { mode: command.mode },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: true };
    }
    case 'OPEN_RESUME': {
      apply((current) => ({
        ...current,
        selection: { ...current.selection, resumeOpen: true, contactOpen: false },
      }));
      return { accepted: true };
    }
    case 'OPEN_CONTACT': {
      apply((current) => ({
        ...current,
        selection: { ...current.selection, contactOpen: true, resumeOpen: false },
      }));
      return { accepted: true };
    }
    case 'RETRY_ASSET': {
      return { accepted: true, reason: 'QUEUED_FOR_LOADER' };
    }
    case 'SKIP_CINEMATIC': {
      const nav = useAppStore.getState().navigation;
      if (nav.phase === 'TRANSITIONING' || nav.phase === 'REQUESTED') {
        const arrived = reduceNavigation(nav, { type: 'ARRIVE' });
        const activated = reduceNavigation(arrived.state, { type: 'ACTIVATE' });
        apply((current) => ({ ...current, navigation: activated.state }));
        publish({
          type: 'ROOM_ENTERED',
          payload: { roomId: activated.state.currentRoomId },
          correlationId,
          occurredAt: nowIso(),
        });
      }
      return { accepted: true };
    }
    default: {
      publish({
        type: 'COMMAND_REJECTED',
        payload: { commandType: 'UNKNOWN', reason: 'UNKNOWN_COMMAND' },
        correlationId,
        occurredAt: nowIso(),
      });
      return { accepted: false, reason: 'UNKNOWN_COMMAND' };
    }
  }
}

export function completeNavigationTransition(): void {
  const nav = useAppStore.getState().navigation;
  const transitioning = reduceNavigation(nav, { type: 'BEGIN_TRANSITION' });
  if (transitioning.accepted) {
    useAppStore.getState().replace({
      ...useAppStore.getState(),
      navigation: transitioning.state,
    });
  }
  const current = useAppStore.getState().navigation;
  const arrived = reduceNavigation(current, { type: 'ARRIVE' });
  if (!arrived.accepted) {
    return;
  }
  const activated = reduceNavigation(arrived.state, { type: 'ACTIVATE' });
  useAppStore.getState().replace({
    ...useAppStore.getState(),
    navigation: activated.state,
    session: { ...useAppStore.getState().session, currentRoomId: activated.state.currentRoomId },
  });
  publish({
    type: 'ROOM_ENTERED',
    payload: { roomId: activated.state.currentRoomId },
    correlationId: createCorrelationId('nav-complete'),
    occurredAt: nowIso(),
  });
}
