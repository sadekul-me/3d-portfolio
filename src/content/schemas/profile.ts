import { z } from 'zod';

import {
  contentVisibilitySchema,
  localizedTextSchema,
  publicationStatusSchema,
} from '@/content/schemas/common';

export const profileSchema = z
  .object({
    id: z.literal('owner'),
    publicationStatus: publicationStatusSchema,
    displayName: z.string().min(1),
    headline: localizedTextSchema,
    summary: localizedTextSchema,
    focusAreas: z.array(localizedTextSchema),
    location: localizedTextSchema.optional(),
    professionalLinks: z.array(
      z
        .object({
          id: z.string().min(1),
          label: localizedTextSchema,
          url: z.string().url(),
          rel: z.enum(['nofollow', 'me']).optional(),
        })
        .strict(),
    ),
    resumeAssetId: z.string().min(1).optional(),
    contactEmail: z.string().email().optional(),
    visibility: contentVisibilitySchema,
  })
  .strict();
