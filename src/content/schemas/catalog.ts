import { z } from 'zod';

import { ROOM_IDS } from '@/types/ids';

import { architectureCaseSchema } from '@/content/schemas/architecture';
import { publicationStatusSchema } from '@/content/schemas/common';
import { profileSchema } from '@/content/schemas/profile';
import { projectSchema, tagSchema } from '@/content/schemas/project';
import { roomDefinitionSchema } from '@/content/schemas/room';
import {
  achievementSchema,
  educationSchema,
  experienceSchema,
  skillSchema,
} from '@/content/schemas/skill';

export const sceneBindingSchema = z
  .object({
    sceneObjectId: z.string().min(1),
    roomId: z.enum(ROOM_IDS),
    entityType: z.enum(['project', 'skill', 'architecture-case', 'experience', 'profile']),
    entityId: z.string().min(1),
  })
  .strict();

export const mediaAssetSchema = z
  .object({
    id: z.string().min(1),
    kind: z.enum(['image', 'video', 'audio', 'document', 'model']),
    src: z.string().min(1),
    publicationStatus: publicationStatusSchema,
  })
  .strict();

export const catalogSchema = z
  .object({
    version: z.string().min(1),
    profile: profileSchema,
    rooms: z.array(roomDefinitionSchema).min(1),
    skills: z.array(skillSchema),
    experiences: z.array(experienceSchema),
    education: z.array(educationSchema),
    achievements: z.array(achievementSchema),
    projects: z.array(projectSchema),
    architectureCases: z.array(architectureCaseSchema),
    tags: z.array(tagSchema),
    mediaAssets: z.array(mediaAssetSchema),
    sceneBindings: z.array(sceneBindingSchema),
  })
  .strict();

export type RawCatalog = z.input<typeof catalogSchema>;
export type ParsedCatalog = z.output<typeof catalogSchema>;
