import type { ArchitectureCaseId, AssetId, ProjectId, RoomId, SkillId } from '@/types/ids';
import type { ExperienceMode, QualityPreset } from '@/types/experience';
import type { Locale } from '@/types/locale';

export type CommandSource = 'user' | 'ai' | 'system' | 'recovery';

type CommandBase = {
  source?: CommandSource;
};

export type AppCommand =
  | (CommandBase & { type: 'NAVIGATE_TO_ROOM'; roomId: RoomId })
  | (CommandBase & { type: 'OPEN_PROJECT'; projectId: ProjectId })
  | (CommandBase & { type: 'CLOSE_PROJECT' })
  | (CommandBase & { type: 'SHOW_SKILL'; skillId: SkillId })
  | (CommandBase & { type: 'SHOW_ARCHITECTURE'; architectureCaseId: ArchitectureCaseId })
  | (CommandBase & { type: 'SET_LANGUAGE'; locale: Locale })
  | (CommandBase & { type: 'SET_QUALITY'; preset: QualityPreset })
  | (CommandBase & { type: 'SET_SOUND'; enabled: boolean })
  | (CommandBase & { type: 'SET_EXPERIENCE_MODE'; mode: ExperienceMode })
  | (CommandBase & { type: 'OPEN_RESUME' })
  | (CommandBase & { type: 'OPEN_CONTACT' })
  | (CommandBase & { type: 'RETRY_ASSET'; assetId: AssetId })
  | (CommandBase & { type: 'SKIP_CINEMATIC' });

export type AppCommandType = AppCommand['type'];
