import { z } from 'zod';

import {
  contentVisibilitySchema,
  localizedTextSchema,
  publicationStatusSchema,
} from '@/content/schemas/common';

export const skillCategorySchema = z.enum([
  'languages',
  'frontend',
  'backend',
  'ai-systems',
  'architecture',
  'cloud',
  'mobile',
  'tooling',
  'leadership',
]);

/**
 * Skills are evidence-backed. There is no proficiency percentage field.
 * Evidence is derived from project, experience, and architecture relations.
 */
export const skillSchema = z
  .object({
    id: z.string().min(1),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    name: localizedTextSchema,
    category: skillCategorySchema,
    summary: localizedTextSchema,
    publicationStatus: publicationStatusSchema,
    visibility: contentVisibilitySchema,
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();

export const experienceSchema = z
  .object({
    id: z.string().min(1),
    organization: localizedTextSchema,
    role: localizedTextSchema,
    summary: localizedTextSchema,
    startDate: z.string().regex(/^\d{4}(-\d{2})?$/),
    endDate: z.union([z.string().regex(/^\d{4}(-\d{2})?$/), z.literal('present')]),
    skillIds: z.array(z.string().min(1)),
    projectIds: z.array(z.string().min(1)),
    publicationStatus: publicationStatusSchema,
    visibility: contentVisibilitySchema,
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();

export const educationSchema = z
  .object({
    id: z.string().min(1),
    institution: localizedTextSchema,
    credential: localizedTextSchema,
    summary: localizedTextSchema.optional(),
    startDate: z.string().regex(/^\d{4}(-\d{2})?$/),
    endDate: z.union([z.string().regex(/^\d{4}(-\d{2})?$/), z.literal('present')]),
    publicationStatus: publicationStatusSchema,
    visibility: contentVisibilitySchema,
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();

export const achievementSchema = z
  .object({
    id: z.string().min(1),
    title: localizedTextSchema,
    summary: localizedTextSchema,
    relatedProjectIds: z.array(z.string().min(1)),
    relatedSkillIds: z.array(z.string().min(1)),
    publicationStatus: publicationStatusSchema,
    visibility: contentVisibilitySchema,
    displayOrder: z.number().int().nonnegative(),
  })
  .strict();
