import type { ArchitectureCaseId, ProjectId, SkillId } from '@/types/ids';
import type { ExperienceMode, QualityPreset } from '@/types/experience';
import type { Locale } from '@/types/locale';
import type { SessionContext } from '@/ai/context/sessionContext';
import type { NavigationSnapshot } from '@/navigation/fsm/navigationFsm';
import { createNavigationSnapshot } from '@/navigation/fsm/navigationFsm';
import { FALLBACK_ROOM_ID } from '@/navigation/graph/resolvePath';
import { FALLBACK_LOCALE } from '@/types/locale';
import { createDefaultSessionContext } from '@/ai/context/sessionContext';

export type SelectionState = {
  projectId: ProjectId | null;
  skillId: SkillId | null;
  architectureCaseId: ArchitectureCaseId | null;
  resumeOpen: boolean;
  contactOpen: boolean;
};

export type PreferencesState = {
  locale: Locale;
  soundEnabled: boolean;
  qualityPreset: QualityPreset;
  experienceModeOverride: ExperienceMode | null;
  reducedMotion: boolean;
};

export type AppStoreState = {
  navigation: NavigationSnapshot;
  preferences: PreferencesState;
  selection: SelectionState;
  session: SessionContext;
};

export const initialSelectionState: SelectionState = {
  projectId: null,
  skillId: null,
  architectureCaseId: null,
  resumeOpen: false,
  contactOpen: false,
};

export function createInitialPreferences(reducedMotion = false): PreferencesState {
  return {
    locale: FALLBACK_LOCALE,
    soundEnabled: false,
    qualityPreset: 'AUTO',
    experienceModeOverride: null,
    reducedMotion,
  };
}

export function createInitialAppState(reducedMotion = false): AppStoreState {
  const preferences = createInitialPreferences(reducedMotion);
  return {
    navigation: createNavigationSnapshot(FALLBACK_ROOM_ID),
    preferences,
    selection: initialSelectionState,
    session: createDefaultSessionContext(preferences.locale),
  };
}
