import type { Locale } from '@/types/locale';
import type { RoomId } from '@/types/ids';

export type VisitorType = 'recruiter' | 'technical' | 'client' | 'unknown';
export type VisitorIntent = 'hire' | 'explore' | 'evaluate' | 'contact' | 'unknown';
export type DepthPreference = 'quick' | 'standard' | 'deep';

/**
 * Privacy-safe in-memory session context. Not a durable profile.
 * Explicit user intent always outweighs inferred behavior.
 */
export type SessionContext = {
  visitorType: VisitorType;
  intent: VisitorIntent;
  interests: string[];
  depthPreference: DepthPreference;
  language: Locale;
  motionPreference: 'standard' | 'reduced';
  currentRoomId: RoomId | null;
};

export function createDefaultSessionContext(language: Locale): SessionContext {
  return {
    visitorType: 'unknown',
    intent: 'unknown',
    interests: [],
    depthPreference: 'standard',
    language,
    motionPreference: 'standard',
    currentRoomId: null,
  };
}
