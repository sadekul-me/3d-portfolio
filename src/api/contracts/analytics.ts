import { z } from 'zod';

export const analyticsEventSchema = z
  .object({
    name: z.string().min(1).max(80),
    timestamp: z.string().datetime(),
    correlationId: z.string().optional(),
    properties: z.record(z.union([z.string(), z.number(), z.boolean()])).optional(),
  })
  .strict();

export const analyticsBatchSchema = z
  .object({
    events: z.array(analyticsEventSchema).min(1).max(25),
  })
  .strict();
