import { z } from 'zod';

import { localeSchema } from '@/content/schemas/common';

export const contactRequestSchema = z
  .object({
    name: z.string().min(1).max(120),
    email: z.string().email().max(254),
    message: z.string().min(1).max(5000),
    locale: localeSchema,
    website: z.string().max(0).optional(),
  })
  .strict();

export const contactResponseSchema = z
  .object({
    requestId: z.string().min(1),
    status: z.enum(['accepted']),
  })
  .strict();

export type ContactRequest = z.infer<typeof contactRequestSchema>;
export type ContactResponse = z.infer<typeof contactResponseSchema>;
