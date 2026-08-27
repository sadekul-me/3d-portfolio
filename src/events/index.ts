import { eventBus } from '@/events/bus/eventBus';
import { recordEvent } from '@/events/debug/eventHistory';

let debugAttached = false;

export function attachDevelopmentEventDebug(): void {
  if (debugAttached || !import.meta.env.DEV) {
    return;
  }
  debugAttached = true;
  const types = [
    'ROOM_ENTERED',
    'NAVIGATION_REJECTED',
    'PROJECT_OPENED',
    'LANGUAGE_CHANGED',
    'ASSET_FAILED',
    'AI_INTENTION_REJECTED',
    'SYSTEM_ERROR',
    'COMMAND_REJECTED',
  ] as const;

  for (const type of types) {
    eventBus.subscribe(type, (event) => {
      recordEvent(event);
    });
  }
}

export { EventBus, eventBus } from '@/events/bus/eventBus';
export type { DomainEvent, DomainEventType, EventOf } from '@/events/types/eventTypes';
export { getEventHistory, clearEventHistory } from '@/events/debug/eventHistory';
