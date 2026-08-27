import type { ArchitectureCaseId, CorrelationId, ProjectId, RoomId, SkillId } from '@/types/ids';
import type { AssetId } from '@/types/ids';
import type { ExperienceMode, QualityPreset } from '@/types/experience';
import type { Locale } from '@/types/locale';
import type { ErrorCategory, ErrorSeverity } from '@/observability/errors/taxonomy';

type EventBase<TType extends string, TPayload> = {
  type: TType;
  payload: TPayload;
  correlationId: CorrelationId;
  occurredAt: string;
};

export type DomainEvent =
  | EventBase<'ROOM_ENTERED', { roomId: RoomId }>
  | EventBase<'ROOM_EXITED', { roomId: RoomId }>
  | EventBase<'NAVIGATION_REJECTED', { target: string; reason: string }>
  | EventBase<'NAVIGATION_INTERRUPTED', { from: RoomId; to: RoomId }>
  | EventBase<'PROJECT_OPENED', { projectId: ProjectId }>
  | EventBase<'PROJECT_CLOSED', { projectId: ProjectId }>
  | EventBase<'SKILL_SHOWN', { skillId: SkillId }>
  | EventBase<'ARCHITECTURE_SHOWN', { architectureCaseId: ArchitectureCaseId }>
  | EventBase<'LANGUAGE_CHANGED', { locale: Locale }>
  | EventBase<'QUALITY_CHANGED', { preset: QualityPreset }>
  | EventBase<'EXPERIENCE_MODE_CHANGED', { mode: ExperienceMode }>
  | EventBase<'SOUND_CHANGED', { enabled: boolean }>
  | EventBase<'ASSET_QUEUED', { assetId: AssetId }>
  | EventBase<'ASSET_READY', { assetId: AssetId }>
  | EventBase<'ASSET_FAILED', { assetId: AssetId; code: string }>
  | EventBase<'AI_INTENTION_RECEIVED', { action: string }>
  | EventBase<'AI_INTENTION_REJECTED', { action: string; reason: string }>
  | EventBase<'AI_INTENTION_EXECUTED', { action: string }>
  | EventBase<'CONTACT_SUBMITTED', { requestId: string }>
  | EventBase<'CONTACT_FAILED', { requestId: string; code: string }>
  | EventBase<'RECOVERY_APPLIED', { strategy: string }>
  | EventBase<'SYSTEM_ERROR', { category: ErrorCategory; severity: ErrorSeverity; code: string }>
  | EventBase<'COMMAND_REJECTED', { commandType: string; reason: string }>;

export type DomainEventType = DomainEvent['type'];

export type EventOf<T extends DomainEventType> = Extract<DomainEvent, { type: T }>;
