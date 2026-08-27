import { catalogSchema, type ParsedCatalog } from '@/content/schemas/catalog';
import { rawCatalog } from '@/content/seed/raw-catalog';
import { ROOM_IDS } from '@/types/ids';
import type { Result } from '@/lib/result';
import { err, ok } from '@/lib/result';

export type CatalogIssue = {
  code: string;
  message: string;
  path: string;
};

export type CatalogValidationOptions = {
  rejectPlaceholders?: boolean;
};

const DEFAULT_OPTIONS: CatalogValidationOptions = {
  rejectPlaceholders: false,
};

function issue(code: string, message: string, path: string): CatalogIssue {
  return { code, message, path };
}

function uniqueOrIssue(values: string[], code: string, path: string, issues: CatalogIssue[]): void {
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) {
      issues.push(issue(code, `Duplicate value "${value}"`, path));
    }
    seen.add(value);
  }
}

export function validateCatalog(
  input: unknown,
  options: CatalogValidationOptions = DEFAULT_OPTIONS,
): Result<ParsedCatalog, CatalogIssue[]> {
  const parsed = catalogSchema.safeParse(input);
  if (!parsed.success) {
    const issues = parsed.error.issues.map((item) =>
      issue('SCHEMA_INVALID', item.message, item.path.join('.') || '(root)'),
    );
    return err(issues);
  }

  const catalog = parsed.data;
  const issues: CatalogIssue[] = [];
  const rejectPlaceholders = options.rejectPlaceholders === true;

  const roomIds = new Set(catalog.rooms.map((room) => room.id));
  uniqueOrIssue(
    catalog.rooms.map((room) => room.id),
    'DUPLICATE_ROOM_ID',
    'rooms.id',
    issues,
  );

  for (const expected of ROOM_IDS) {
    if (!roomIds.has(expected)) {
      issues.push(issue('MISSING_ROOM', `Required room "${expected}" is not defined`, 'rooms'));
    }
  }

  for (const room of catalog.rooms) {
    if (room.route !== `/experience/${room.id}`) {
      issues.push(
        issue(
          'ROOM_ROUTE_MISMATCH',
          `Room "${room.id}" route must be /experience/${room.id}`,
          `rooms.${room.id}.route`,
        ),
      );
    }
    if (room.adjacentRoomIds.includes(room.id)) {
      issues.push(
        issue(
          'SELF_ADJACENT_ROOM',
          `Room "${room.id}" cannot be adjacent to itself`,
          `rooms.${room.id}`,
        ),
      );
    }
    for (const adjacent of room.adjacentRoomIds) {
      if (!roomIds.has(adjacent)) {
        issues.push(
          issue(
            'UNKNOWN_ADJACENT_ROOM',
            `Room "${room.id}" references missing room "${adjacent}"`,
            `rooms.${room.id}`,
          ),
        );
      }
    }
  }

  const skillIds = new Set(catalog.skills.map((skill) => skill.id));
  uniqueOrIssue(
    catalog.skills.map((skill) => skill.id),
    'DUPLICATE_SKILL_ID',
    'skills.id',
    issues,
  );
  uniqueOrIssue(
    catalog.skills.map((skill) => skill.slug),
    'DUPLICATE_SKILL_SLUG',
    'skills.slug',
    issues,
  );

  const projectIds = new Set(catalog.projects.map((project) => project.id));
  uniqueOrIssue(
    catalog.projects.map((project) => project.id),
    'DUPLICATE_PROJECT_ID',
    'projects.id',
    issues,
  );
  uniqueOrIssue(
    catalog.projects.map((project) => project.slug),
    'DUPLICATE_PROJECT_SLUG',
    'projects.slug',
    issues,
  );

  const architectureIds = new Set(catalog.architectureCases.map((item) => item.id));
  uniqueOrIssue(
    catalog.architectureCases.map((item) => item.id),
    'DUPLICATE_ARCHITECTURE_ID',
    'architectureCases.id',
    issues,
  );
  uniqueOrIssue(
    catalog.architectureCases.map((item) => item.slug),
    'DUPLICATE_ARCHITECTURE_SLUG',
    'architectureCases.slug',
    issues,
  );

  const experienceIds = new Set(catalog.experiences.map((item) => item.id));
  const mediaAssetIds = new Set(catalog.mediaAssets.map((item) => item.id));

  for (const project of catalog.projects) {
    uniqueOrIssue(
      project.skillIds,
      'DUPLICATE_PROJECT_SKILL',
      `projects.${project.id}.skillIds`,
      issues,
    );
    for (const skillId of project.skillIds) {
      if (!skillIds.has(skillId)) {
        issues.push(
          issue(
            'UNKNOWN_SKILL',
            `Project "${project.id}" references missing skill "${skillId}"`,
            `projects.${project.id}`,
          ),
        );
      }
    }
    for (const technologyId of project.technologyIds) {
      if (!skillIds.has(technologyId)) {
        issues.push(
          issue(
            'UNKNOWN_TECHNOLOGY',
            `Project "${project.id}" references missing technology skill "${technologyId}"`,
            `projects.${project.id}`,
          ),
        );
      }
    }
    if (project.architectureCaseId && !architectureIds.has(project.architectureCaseId)) {
      issues.push(
        issue(
          'UNKNOWN_ARCHITECTURE_CASE',
          `Project "${project.id}" references missing architecture case "${project.architectureCaseId}"`,
          `projects.${project.id}`,
        ),
      );
    }
    for (const media of project.media) {
      if (!mediaAssetIds.has(media.assetId)) {
        issues.push(
          issue(
            'UNKNOWN_MEDIA_ASSET',
            `Project "${project.id}" references missing media asset "${media.assetId}"`,
            `projects.${project.id}`,
          ),
        );
      }
    }
  }

  for (const experience of catalog.experiences) {
    for (const skillId of experience.skillIds) {
      if (!skillIds.has(skillId)) {
        issues.push(
          issue(
            'UNKNOWN_SKILL',
            `Experience "${experience.id}" references missing skill "${skillId}"`,
            `experiences.${experience.id}`,
          ),
        );
      }
    }
    for (const projectId of experience.projectIds) {
      if (!projectIds.has(projectId)) {
        issues.push(
          issue(
            'UNKNOWN_PROJECT',
            `Experience "${experience.id}" references missing project "${projectId}"`,
            `experiences.${experience.id}`,
          ),
        );
      }
    }
  }

  for (const architectureCase of catalog.architectureCases) {
    const nodeIds = new Set(architectureCase.nodes.map((node) => node.id));
    uniqueOrIssue(
      architectureCase.nodes.map((node) => node.id),
      'DUPLICATE_ARCHITECTURE_NODE',
      `architectureCases.${architectureCase.id}.nodes`,
      issues,
    );
    uniqueOrIssue(
      architectureCase.edges.map((edge) => edge.id),
      'DUPLICATE_ARCHITECTURE_EDGE',
      `architectureCases.${architectureCase.id}.edges`,
      issues,
    );

    for (const edge of architectureCase.edges) {
      if (!nodeIds.has(edge.from) || !nodeIds.has(edge.to)) {
        issues.push(
          issue(
            'BROKEN_ARCHITECTURE_EDGE',
            `Architecture case "${architectureCase.id}" edge "${edge.id}" references a missing node`,
            `architectureCases.${architectureCase.id}.edges`,
          ),
        );
      }
    }

    for (const flow of architectureCase.flows) {
      for (const nodeId of flow.nodeIds) {
        if (!nodeIds.has(nodeId)) {
          issues.push(
            issue(
              'BROKEN_ARCHITECTURE_FLOW',
              `Architecture case "${architectureCase.id}" flow "${flow.id}" references missing node "${nodeId}"`,
              `architectureCases.${architectureCase.id}.flows`,
            ),
          );
        }
      }
    }

    for (const projectId of architectureCase.relatedProjectIds) {
      if (!projectIds.has(projectId)) {
        issues.push(
          issue(
            'UNKNOWN_PROJECT',
            `Architecture case "${architectureCase.id}" references missing project "${projectId}"`,
            `architectureCases.${architectureCase.id}`,
          ),
        );
      }
    }

    for (const skillId of architectureCase.relatedSkillIds) {
      if (!skillIds.has(skillId)) {
        issues.push(
          issue(
            'UNKNOWN_SKILL',
            `Architecture case "${architectureCase.id}" references missing skill "${skillId}"`,
            `architectureCases.${architectureCase.id}`,
          ),
        );
      }
    }
  }

  for (const binding of catalog.sceneBindings) {
    if (!roomIds.has(binding.roomId)) {
      issues.push(
        issue(
          'BROKEN_SCENE_BINDING',
          `Scene object "${binding.sceneObjectId}" binds to unknown room "${binding.roomId}"`,
          'sceneBindings',
        ),
      );
    }

    const exists =
      (binding.entityType === 'project' && projectIds.has(binding.entityId)) ||
      (binding.entityType === 'skill' && skillIds.has(binding.entityId)) ||
      (binding.entityType === 'architecture-case' && architectureIds.has(binding.entityId)) ||
      (binding.entityType === 'experience' && experienceIds.has(binding.entityId)) ||
      (binding.entityType === 'profile' && binding.entityId === catalog.profile.id);

    if (!exists) {
      issues.push(
        issue(
          'BROKEN_SCENE_BINDING',
          `Scene object "${binding.sceneObjectId}" binds to missing ${binding.entityType} "${binding.entityId}"`,
          'sceneBindings',
        ),
      );
    }
  }

  if (rejectPlaceholders) {
    const placeholderEntities: Array<{ path: string; status: string }> = [
      { path: 'profile', status: catalog.profile.publicationStatus },
      ...catalog.skills.map((item) => ({
        path: `skills.${item.id}`,
        status: item.publicationStatus,
      })),
      ...catalog.projects.map((item) => ({
        path: `projects.${item.id}`,
        status: item.publicationStatus,
      })),
      ...catalog.experiences.map((item) => ({
        path: `experiences.${item.id}`,
        status: item.publicationStatus,
      })),
    ];
    for (const entity of placeholderEntities) {
      if (entity.status === 'placeholder') {
        issues.push(
          issue(
            'PLACEHOLDER_NOT_ALLOWED',
            'Placeholder content is not allowed in production publication',
            entity.path,
          ),
        );
      }
    }
  }

  if (issues.length > 0) {
    return err(issues);
  }

  return ok(catalog);
}

export function validateSeedCatalog(
  options: CatalogValidationOptions = DEFAULT_OPTIONS,
): Result<ParsedCatalog, CatalogIssue[]> {
  return validateCatalog(rawCatalog, options);
}
