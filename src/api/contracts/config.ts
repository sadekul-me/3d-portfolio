import { z } from 'zod';

export const publicConfigSchema = z
  .object({
    aiEnabled: z.boolean(),
    contactEnabled: z.boolean(),
    diagnosticsEnabled: z.boolean(),
    assetManifestVersion: z.string(),
  })
  .strict();

export const healthSchema = z
  .object({
    status: z.enum(['ok', 'degraded', 'down']),
    checks: z.record(z.enum(['ok', 'degraded', 'down'])),
  })
  .strict();
