import { getSkillEvidence, loadCatalog } from '@/content/repositories/catalogRepository';
import { localizedValue, type Locale } from '@/types/locale';
import type { RoomId } from '@/types/ids';

export function selectRoomTitle(roomId: RoomId, locale: Locale): string {
  const room = loadCatalog().rooms.find((item) => item.id === roomId);
  if (!room) {
    return roomId;
  }
  return localizedValue(room.title, locale);
}

export function selectFeaturedProjects(locale: Locale) {
  return loadCatalog()
    .projects.filter((project) => project.featured)
    .sort((left, right) => left.displayOrder - right.displayOrder)
    .map((project) => ({
      id: project.id,
      slug: project.slug,
      title: localizedValue(project.title, locale),
      summary: localizedValue(project.summary, locale),
    }));
}

export function selectSkillCard(skillId: string, locale: Locale) {
  const catalog = loadCatalog();
  const skill = catalog.skills.find((item) => item.id === skillId);
  if (!skill) {
    return null;
  }
  const evidence = getSkillEvidence(skillId, catalog);
  return {
    id: skill.id,
    slug: skill.slug,
    name: localizedValue(skill.name, locale),
    summary: localizedValue(skill.summary, locale),
    category: skill.category,
    evidenceCount:
      evidence.projectIds.length +
      evidence.experienceIds.length +
      evidence.architectureCaseIds.length,
    evidence,
  };
}
