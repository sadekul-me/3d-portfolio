import { validateSeedCatalog } from '@/content/validation/validateCatalog';
import type { ParsedCatalog } from '@/content/schemas/catalog';
import type { SkillEvidence } from '@/content/domain/models';
import { asArchitectureCaseId, asExperienceId, asProjectId, asSkillId } from '@/types/ids';
import { isAiIndexable, isPubliclyListed, isSearchIndexable } from '@/types/visibility';

let cachedCatalog: ParsedCatalog | null = null;

export function loadCatalog(): ParsedCatalog {
  if (cachedCatalog) {
    return cachedCatalog;
  }
  const result = validateSeedCatalog();
  if (!result.ok) {
    const details = result.error.map((issue) => `${issue.code}: ${issue.message}`).join('; ');
    throw new Error(`Canonical catalog is invalid: ${details}`);
  }
  cachedCatalog = result.value;
  return cachedCatalog;
}

/** Test-only: drop the memoized catalog after mutating seed fixtures. */
export function resetCatalogCache(): void {
  cachedCatalog = null;
}

export function getPublicProjects(catalog = loadCatalog()): ParsedCatalog['projects'] {
  return catalog.projects.filter((project) =>
    isPubliclyListed(project.visibility, project.publicationStatus),
  );
}

export function getSearchableEntities(catalog = loadCatalog()) {
  const published = {
    profile: isSearchIndexable(catalog.profile.visibility, catalog.profile.publicationStatus)
      ? catalog.profile
      : null,
    skills: catalog.skills.filter((item) =>
      isSearchIndexable(item.visibility, item.publicationStatus),
    ),
    projects: catalog.projects.filter((item) =>
      isSearchIndexable(item.visibility, item.publicationStatus),
    ),
    experiences: catalog.experiences.filter((item) =>
      isSearchIndexable(item.visibility, item.publicationStatus),
    ),
    architectureCases: catalog.architectureCases.filter((item) =>
      isSearchIndexable(item.visibility, item.publicationStatus),
    ),
  };
  return published;
}

export function getAiIndexableEntities(catalog = loadCatalog()) {
  return {
    profile: isAiIndexable(catalog.profile.visibility, catalog.profile.publicationStatus)
      ? catalog.profile
      : null,
    skills: catalog.skills.filter((item) => isAiIndexable(item.visibility, item.publicationStatus)),
    projects: catalog.projects.filter((item) =>
      isAiIndexable(item.visibility, item.publicationStatus),
    ),
    experiences: catalog.experiences.filter((item) =>
      isAiIndexable(item.visibility, item.publicationStatus),
    ),
    architectureCases: catalog.architectureCases.filter((item) =>
      isAiIndexable(item.visibility, item.publicationStatus),
    ),
  };
}

export function getSkillEvidence(skillId: string, catalog = loadCatalog()): SkillEvidence {
  const branded = asSkillId(skillId);
  return {
    skillId: branded,
    projectIds: catalog.projects
      .filter(
        (project) => project.skillIds.includes(skillId) || project.technologyIds.includes(skillId),
      )
      .map((project) => asProjectId(project.id)),
    experienceIds: catalog.experiences
      .filter((experience) => experience.skillIds.includes(skillId))
      .map((experience) => asExperienceId(experience.id)),
    architectureCaseIds: catalog.architectureCases
      .filter((architectureCase) => architectureCase.relatedSkillIds.includes(skillId))
      .map((architectureCase) => asArchitectureCaseId(architectureCase.id)),
  };
}

export function getProjectBySlug(slug: string, catalog = loadCatalog()) {
  return catalog.projects.find((project) => project.slug === slug);
}

export function getRoomById(roomId: ParsedCatalog['rooms'][number]['id'], catalog = loadCatalog()) {
  return catalog.rooms.find((room) => room.id === roomId);
}
