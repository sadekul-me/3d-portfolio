import type { DomainEvent, DomainEventType, EventOf } from '@/events/types/eventTypes';
import type { TelemetryService } from '@/observability/telemetry/types';

export type Unsubscribe = () => void;
type Handler<T extends DomainEvent> = (event: T) => void;

/**
 * Lightweight synchronous event bus.
 * Subscribers must not become the source of truth.
 * High-frequency pointer/camera/frame data is forbidden here by type design.
 */
export class EventBus {
  private readonly listeners = new Map<DomainEventType, Set<Handler<DomainEvent>>>();
  private readonly telemetry: TelemetryService | undefined;

  constructor(telemetry?: TelemetryService) {
    this.telemetry = telemetry;
  }

  subscribe<T extends DomainEventType>(type: T, handler: Handler<EventOf<T>>): Unsubscribe {
    const set = this.listeners.get(type) ?? new Set();
    set.add(handler as Handler<DomainEvent>);
    this.listeners.set(type, set);

    return () => {
      const current = this.listeners.get(type);
      current?.delete(handler as Handler<DomainEvent>);
      if (current && current.size === 0) {
        this.listeners.delete(type);
      }
    };
  }

  publish(event: DomainEvent): void {
    const handlers = this.listeners.get(event.type);
    if (!handlers || handlers.size === 0) {
      return;
    }

    for (const handler of [...handlers]) {
      try {
        handler(event);
      } catch (error) {
        this.telemetry?.reportError({
          code: 'EVENT_SUBSCRIBER_FAILED',
          category: 'APP',
          severity: 'ERROR',
          recoverable: true,
          visitorMessageKey: 'errors.generic',
          technicalMessage: error instanceof Error ? error.message : 'Unknown subscriber failure',
          correlationId: event.correlationId,
          context: { eventType: event.type },
        });
      }
    }
  }

  clear(): void {
    this.listeners.clear();
  }
}

export const eventBus = new EventBus();
