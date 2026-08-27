import { z } from 'zod';

export const apiErrorSchema = z
  .object({
    code: z.string().min(1),
    message: z.string().min(1),
    requestId: z.string().min(1),
    details: z.array(z.string()).optional(),
  })
  .strict();

export const apiMetaSchema = z
  .object({
    requestId: z.string().min(1),
    correlationId: z.string().min(1).optional(),
  })
  .strict();

export type ApiErrorBody = z.infer<typeof apiErrorSchema>;
