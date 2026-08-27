import { getSearchableEntities, loadCatalog } from '@/content/repositories/catalogRepository';
import { localizedValue, type Locale } from '@/types/locale';

export type SearchDocumentType = 'profile' | 'skill' | 'project' | 'experience' | 'architecture';

export type SearchDocument = {
  id: string;
  type: SearchDocumentType;
  title: string;
  summary: string;
  tokens: string[];
  href: string;
};

function tokenize(...parts: string[]): string[] {
  return parts
    .join(' ')
    .toLowerCase()
    .split(/[^\p{L}\p{N}]+/u)
    .filter((token) => token.length > 1);
}

export function buildSearchIndex(locale: Locale, catalog = loadCatalog()): SearchDocument[] {
  const searchable = getSearchableEntities(catalog);
  const documents: SearchDocument[] = [];

  if (searchable.profile) {
    documents.push({
      id: searchable.profile.id,
      type: 'profile',
      title: searchable.profile.displayName,
      summary: localizedValue(searchable.profile.summary, locale),
      tokens: tokenize(
        searchable.profile.displayName,
        localizedValue(searchable.profile.headline, locale),
        localizedValue(searchable.profile.summary, locale),
      ),
      href: '/portfolio/about',
    });
  }

  for (const skill of searchable.skills) {
    documents.push({
      id: skill.id,
      type: 'skill',
      title: localizedValue(skill.name, locale),
      summary: localizedValue(skill.summary, locale),
      tokens: tokenize(
        localizedValue(skill.name, locale),
        localizedValue(skill.summary, locale),
        skill.slug,
      ),
      href: '/portfolio/skills',
    });
  }

  for (const project of searchable.projects) {
    documents.push({
      id: project.id,
      type: 'project',
      title: localizedValue(project.title, locale),
      summary: localizedValue(project.summary, locale),
      tokens: tokenize(
        localizedValue(project.title, locale),
        localizedValue(project.summary, locale),
        localizedValue(project.problem, locale),
        project.slug,
      ),
      href: `/portfolio/projects/${project.slug}`,
    });
  }

  for (const experience of searchable.experiences) {
    documents.push({
      id: experience.id,
      type: 'experience',
      title: localizedValue(experience.role, locale),
      summary: localizedValue(experience.summary, locale),
      tokens: tokenize(
        localizedValue(experience.role, locale),
        localizedValue(experience.organization, locale),
        localizedValue(experience.summary, locale),
      ),
      href: '/portfolio/experience',
    });
  }

  for (const architectureCase of searchable.architectureCases) {
    documents.push({
      id: architectureCase.id,
      type: 'architecture',
      title: localizedValue(architectureCase.title, locale),
      summary: localizedValue(architectureCase.summary, locale),
      tokens: tokenize(
        localizedValue(architectureCase.title, locale),
        localizedValue(architectureCase.summary, locale),
        architectureCase.slug,
      ),
      href: '/portfolio/architecture',
    });
  }

  return documents;
}

export function searchCatalog(
  query: string,
  locale: Locale,
  documents = buildSearchIndex(locale),
): SearchDocument[] {
  const terms = tokenize(query);
  if (terms.length === 0) {
    return [];
  }
  return documents
    .map((document) => {
      const hits = terms.filter((term) =>
        document.tokens.some((token) => token.includes(term)),
      ).length;
      return { document, hits };
    })
    .filter((item) => item.hits > 0)
    .sort((left, right) => right.hits - left.hits)
    .map((item) => item.document);
}
