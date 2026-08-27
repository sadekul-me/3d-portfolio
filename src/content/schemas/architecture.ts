import { z } from 'zod';

import {
  contentVisibilitySchema,
  localizedTextSchema,
  publicationStatusSchema,
} from '@/content/schemas/common';

export const architectureNodeKindSchema = z.enum([
  'system',
  'service',
  'store',
  'client',
  'provider',
  'boundary',
  'decision',
]);

export const architectureNodeSchema = z
  .object({
    id: z.string().min(1),
    label: localizedTextSchema,
    kind: architectureNodeKindSchema,
    summary: localizedTextSchema,
    responsibility: localizedTextSchema,
  })
  .strict();

export const architectureEdgeSchema = z
  .object({
    id: z.string().min(1),
    from: z.string().min(1),
    to: z.string().min(1),
    label: localizedTextSchema.optional(),
    bidirectional: z.boolean().default(false),
  })
  .strict();

export const architectureFlowSchema = z
  .object({
    id: z.string().min(1),
    title: localizedTextSchema,
    summary: localizedTextSchema,
    nodeIds: z.array(z.string().min(1)).min(2),
  })
  .strict();

export const architectureDecisionSchema = z
  .object({
    id: z.string().min(1),
    title: localizedTextSchema,
    rationale: localizedTextSchema,
    tradeOffs: z.array(localizedTextSchema),
    relatedNodeIds: z.array(z.string().min(1)),
  })
  .strict();

/**
 * Graph-oriented architecture case studies are reusable by 2D diagrams and 3D presentations.
 */
export const architectureCaseSchema = z
  .object({
    id: z.string().min(1),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    title: localizedTextSchema,
    summary: localizedTextSchema,
    relatedProjectIds: z.array(z.string().min(1)),
    relatedSkillIds: z.array(z.string().min(1)),
    nodes: z.array(architectureNodeSchema),
    edges: z.array(architectureEdgeSchema),
    flows: z.array(architectureFlowSchema),
    decisions: z.array(architectureDecisionSchema),
    publicationStatus: publicationStatusSchema,
    visibility: contentVisibilitySchema,
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();
