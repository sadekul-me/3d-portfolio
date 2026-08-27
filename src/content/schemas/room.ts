import { z } from 'zod';

import { ROOM_IDS } from '@/types/ids';

import {
  experienceModeSchema,
  qualityPresetSchema,
  requiredLocalizedTextSchema,
} from '@/content/schemas/common';

export const preloadPrioritySchema = z.enum(['critical', 'high', 'normal', 'low']);

export const roomCapabilitySchema = z.enum([
  'cinematic-intro',
  'spatial-ui',
  'guided-navigation',
  'audio',
  'ai-visualization',
  'architecture-graph',
  'project-media',
  'contact',
  'identity-timeline',
  'skill-evidence',
]);

export const roomDefinitionSchema = z
  .object({
    id: z.enum(ROOM_IDS),
    route: z.string().regex(/^\/experience\/[a-z0-9-]+$/),
    title: requiredLocalizedTextSchema,
    purpose: requiredLocalizedTextSchema,
    preloadPriority: preloadPrioritySchema,
    qualityCompatibility: z.array(qualityPresetSchema).min(1),
    adjacentRoomIds: z.array(z.enum(ROOM_IDS)),
    assetManifestId: z.string().min(1).optional(),
    capabilities: z.array(roomCapabilitySchema),
    fallbackMode: experienceModeSchema,
    sceneModule: z.string().min(1),
  })
  .strict();

export const roomCatalogSchema = z.array(roomDefinitionSchema).min(1);
