import { brand, type Brand } from '@/types/brand';

export type ProjectId = Brand<string, 'ProjectId'>;
export type SkillId = Brand<string, 'SkillId'>;
export type AssetId = Brand<string, 'AssetId'>;
export type ArchitectureCaseId = Brand<string, 'ArchitectureCaseId'>;
export type ArchitectureNodeId = Brand<string, 'ArchitectureNodeId'>;
export type ExperienceId = Brand<string, 'ExperienceId'>;
export type EducationId = Brand<string, 'EducationId'>;
export type AchievementId = Brand<string, 'AchievementId'>;
export type MediaAssetId = Brand<string, 'MediaAssetId'>;
export type TagId = Brand<string, 'TagId'>;
export type CorrelationId = Brand<string, 'CorrelationId'>;
export type SessionId = Brand<string, 'SessionId'>;
export type SceneObjectId = Brand<string, 'SceneObjectId'>;

export const ROOM_IDS = [
  'exterior',
  'identity',
  'engineering',
  'ai-lab',
  'projects',
  'architecture',
  'command-center',
] as const;

export type RoomId = (typeof ROOM_IDS)[number];

export function isRoomId(value: string): value is RoomId {
  return (ROOM_IDS as readonly string[]).includes(value);
}

export function asProjectId(value: string): ProjectId {
  return brand<string, 'ProjectId'>(value);
}

export function asSkillId(value: string): SkillId {
  return brand<string, 'SkillId'>(value);
}

export function asAssetId(value: string): AssetId {
  return brand<string, 'AssetId'>(value);
}

export function asArchitectureCaseId(value: string): ArchitectureCaseId {
  return brand<string, 'ArchitectureCaseId'>(value);
}

export function asArchitectureNodeId(value: string): ArchitectureNodeId {
  return brand<string, 'ArchitectureNodeId'>(value);
}

export function asExperienceId(value: string): ExperienceId {
  return brand<string, 'ExperienceId'>(value);
}

export function asEducationId(value: string): EducationId {
  return brand<string, 'EducationId'>(value);
}

export function asAchievementId(value: string): AchievementId {
  return brand<string, 'AchievementId'>(value);
}

export function asMediaAssetId(value: string): MediaAssetId {
  return brand<string, 'MediaAssetId'>(value);
}

export function asTagId(value: string): TagId {
  return brand<string, 'TagId'>(value);
}

export function asCorrelationId(value: string): CorrelationId {
  return brand<string, 'CorrelationId'>(value);
}

export function asSessionId(value: string): SessionId {
  return brand<string, 'SessionId'>(value);
}

export function asSceneObjectId(value: string): SceneObjectId {
  return brand<string, 'SceneObjectId'>(value);
}
