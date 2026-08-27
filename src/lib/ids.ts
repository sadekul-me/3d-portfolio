import { asCorrelationId, asSessionId, type CorrelationId, type SessionId } from '@/types/ids';

function randomSegment(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `id-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export function createCorrelationId(prefix = 'corr'): CorrelationId {
  return asCorrelationId(`${prefix}-${randomSegment()}`);
}

export function createAnonymousSessionId(): SessionId {
  return asSessionId(`anon-${randomSegment()}`);
}
