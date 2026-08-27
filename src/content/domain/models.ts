import type { ParsedCatalog } from '@/content/schemas/catalog';
import type { ArchitectureCaseId, ProjectId, SkillId } from '@/types/ids';
import type { ContentVisibility, PublicationStatus } from '@/types/visibility';
import type { LocalizedText } from '@/types/locale';

export type RoomCapability =
  | 'cinematic-intro'
  | 'spatial-ui'
  | 'guided-navigation'
  | 'audio'
  | 'ai-visualization'
  | 'architecture-graph'
  | 'project-media'
  | 'contact'
  | 'identity-timeline'
  | 'skill-evidence';

export type PreloadPriority = 'critical' | 'high' | 'normal' | 'low';

export type RoomDefinition = ParsedCatalog['rooms'][number];

export type SkillEvidence = {
  skillId: SkillId;
  projectIds: ProjectId[];
  experienceIds: string[];
  architectureCaseIds: ArchitectureCaseId[];
};

export type CanonicalCatalog = ParsedCatalog;

export type ContentEntity = {
  publicationStatus: PublicationStatus;
  visibility: ContentVisibility;
};

export type LocalizedField = LocalizedText;
