import { describe, expect, it, vi } from 'vitest';

import { EventBus } from '@/events/bus/eventBus';
import { asCorrelationId } from '@/types/ids';

describe('event bus', () => {
  it('delivers typed events to subscribers', () => {
    const bus = new EventBus();
    const received: string[] = [];
    const unsubscribe = bus.subscribe('ROOM_ENTERED', (event) => {
      received.push(event.payload.roomId);
    });

    bus.publish({
      type: 'ROOM_ENTERED',
      payload: { roomId: 'ai-lab' },
      correlationId: asCorrelationId('test-1'),
      occurredAt: new Date().toISOString(),
    });

    expect(received).toEqual(['ai-lab']);
    unsubscribe();
  });

  it('isolates subscriber failures', () => {
    const reportError = vi.fn();
    const bus = new EventBus({
      log() {},
      metric() {},
      trace: (_name, fn) => fn(),
      traceAsync: async (_name, fn) => fn(),
      reportError,
    });
    const surviving = vi.fn();
    bus.subscribe('LANGUAGE_CHANGED', () => {
      throw new Error('subscriber crashed');
    });
    bus.subscribe('LANGUAGE_CHANGED', surviving);

    bus.publish({
      type: 'LANGUAGE_CHANGED',
      payload: { locale: 'zh-CN' },
      correlationId: asCorrelationId('test-2'),
      occurredAt: new Date().toISOString(),
    });

    expect(surviving).toHaveBeenCalledTimes(1);
    expect(reportError).toHaveBeenCalledTimes(1);
  });

  it('unsubscribes cleanly', () => {
    const bus = new EventBus();
    const handler = vi.fn();
    const unsubscribe = bus.subscribe('PROJECT_OPENED', handler);
    unsubscribe();
    bus.publish({
      type: 'PROJECT_OPENED',
      payload: { projectId: 'p1' as never },
      correlationId: asCorrelationId('test-3'),
      occurredAt: new Date().toISOString(),
    });
    expect(handler).not.toHaveBeenCalled();
  });
});
