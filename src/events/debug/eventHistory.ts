import type { DomainEvent } from '@/events/types/eventTypes';

const MAX_HISTORY = 50;

const history: DomainEvent[] = [];

/**
 * Bounded in-memory history for development debugging only.
 * Never used as application state.
 */
export function recordEvent(event: DomainEvent): void {
  history.push(event);
  if (history.length > MAX_HISTORY) {
    history.shift();
  }
}

export function getEventHistory(): readonly DomainEvent[] {
  return history;
}

export function clearEventHistory(): void {
  history.length = 0;
}
