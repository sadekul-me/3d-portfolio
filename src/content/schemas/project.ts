import { z } from 'zod';

import {
  contentVisibilitySchema,
  localizedTextSchema,
  publicationStatusSchema,
} from '@/content/schemas/common';

export const projectMediaKindSchema = z.enum(['image', 'video', 'diagram', 'document']);

export const projectMediaSchema = z
  .object({
    id: z.string().min(1),
    kind: projectMediaKindSchema,
    assetId: z.string().min(1),
    caption: localizedTextSchema.optional(),
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();

export const projectSchema = z
  .object({
    id: z.string().min(1),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    title: localizedTextSchema,
    summary: localizedTextSchema,
    description: localizedTextSchema,
    problem: localizedTextSchema,
    solution: localizedTextSchema,
    role: localizedTextSchema,
    skillIds: z.array(z.string().min(1)),
    technologyIds: z.array(z.string().min(1)),
    engineeringHighlights: z.array(localizedTextSchema),
    architectureCaseId: z.string().min(1).optional(),
    media: z.array(projectMediaSchema),
    publicLinks: z.array(
      z
        .object({
          id: z.string().min(1),
          label: localizedTextSchema,
          url: z.string().url(),
        })
        .strict(),
    ),
    publicationStatus: publicationStatusSchema,
    visibility: contentVisibilitySchema,
    featured: z.boolean(),
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();

export const tagSchema = z
  .object({
    id: z.string().min(1),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    label: localizedTextSchema,
  })
  .strict();
