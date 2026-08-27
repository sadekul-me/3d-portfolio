import { describe, expect, it } from 'vitest';

import { validateCatalog, validateSeedCatalog } from '@/content/validation/validateCatalog';
import { rawCatalog } from '@/content/seed/raw-catalog';
import { PRIVATE_VISIBILITY } from '@/types/visibility';

describe('canonical content validation', () => {
  it('accepts the foundation seed catalog', () => {
    const result = validateSeedCatalog();
    expect(result.ok).toBe(true);
  });

  it('rejects a project that references a missing skill', () => {
    const result = validateCatalog({
      ...rawCatalog,
      projects: [
        {
          id: 'proj-broken',
          slug: 'broken-project',
          title: { en: '[PLACEHOLDER] Broken', 'zh-CN': '[PLACEHOLDER] 损坏' },
          summary: { en: '[PLACEHOLDER] Summary', 'zh-CN': '[PLACEHOLDER] 摘要' },
          description: { en: '[PLACEHOLDER] Description', 'zh-CN': '[PLACEHOLDER] 描述' },
          problem: { en: '[PLACEHOLDER] Problem', 'zh-CN': '[PLACEHOLDER] 问题' },
          solution: { en: '[PLACEHOLDER] Solution', 'zh-CN': '[PLACEHOLDER] 方案' },
          role: { en: '[PLACEHOLDER] Role', 'zh-CN': '[PLACEHOLDER] 角色' },
          skillIds: ['skill-does-not-exist'],
          technologyIds: [],
          engineeringHighlights: [],
          media: [],
          publicLinks: [],
          publicationStatus: 'placeholder',
          visibility: PRIVATE_VISIBILITY,
          featured: false,
          displayOrder: 0,
        },
      ],
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.some((issue) => issue.code === 'UNKNOWN_SKILL')).toBe(true);
    }
  });

  it('rejects duplicate slugs', () => {
    const skill = {
      id: 'skill-a',
      slug: 'same-slug',
      name: { en: 'A', 'zh-CN': 'A' },
      category: 'frontend' as const,
      summary: { en: 'A', 'zh-CN': 'A' },
      publicationStatus: 'placeholder' as const,
      visibility: PRIVATE_VISIBILITY,
      displayOrder: 0,
    };
    const result = validateCatalog({
      ...rawCatalog,
      skills: [skill, { ...skill, id: 'skill-b' }],
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.some((issue) => issue.code === 'DUPLICATE_SKILL_SLUG')).toBe(true);
    }
  });

  it('rejects a broken architecture edge', () => {
    const result = validateCatalog({
      ...rawCatalog,
      architectureCases: [
        {
          id: 'arch-broken',
          slug: 'broken-arch',
          title: { en: 'Broken', 'zh-CN': '损坏' },
          summary: { en: 'Broken', 'zh-CN': '损坏' },
          relatedProjectIds: [],
          relatedSkillIds: [],
          nodes: [
            {
              id: 'n1',
              label: { en: 'N1', 'zh-CN': 'N1' },
              kind: 'system',
              summary: { en: 'n', 'zh-CN': 'n' },
              responsibility: { en: 'n', 'zh-CN': 'n' },
            },
          ],
          edges: [{ id: 'e1', from: 'n1', to: 'missing-node' }],
          flows: [],
          decisions: [],
          publicationStatus: 'placeholder',
          visibility: PRIVATE_VISIBILITY,
          displayOrder: 0,
        },
      ],
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.some((issue) => issue.code === 'BROKEN_ARCHITECTURE_EDGE')).toBe(true);
    }
  });

  it('fails production publication when placeholders remain', () => {
    const result = validateSeedCatalog({ rejectPlaceholders: true });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.some((issue) => issue.code === 'PLACEHOLDER_NOT_ALLOWED')).toBe(true);
    }
  });
});
