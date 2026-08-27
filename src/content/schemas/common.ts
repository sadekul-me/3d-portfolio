import { z } from 'zod';

import { LOCALES } from '@/types/locale';

export const localeSchema = z.enum(LOCALES);

export const localizedTextSchema = z
  .object({
    en: z.string().min(1),
    'zh-CN': z.string().min(1).optional(),
  })
  .strict();

export const requiredLocalizedTextSchema = z
  .object({
    en: z.string().min(1),
    'zh-CN': z.string().min(1),
  })
  .strict();

export const contentVisibilitySchema = z
  .object({
    public: z.boolean(),
    aiReadable: z.boolean(),
    searchable: z.boolean(),
    internal: z.boolean(),
  })
  .strict();

export const publicationStatusSchema = z.enum(['placeholder', 'draft', 'published']);

export const qualityPresetSchema = z.enum(['AUTO', 'HIGH', 'BALANCED', 'LOW']);

export const experienceModeSchema = z.enum([
  'PREMIUM_3D',
  'REDUCED_3D',
  'LIGHTWEIGHT',
  'QUICK_PORTFOLIO',
  'STATIC_CORE',
]);
