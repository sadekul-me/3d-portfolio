import { z } from 'zod';

import { ROOM_IDS } from '@/types/ids';

export const AI_TOOL_NAMES = [
  'navigate_to_room',
  'open_project',
  'show_skill',
  'show_architecture',
  'open_resume',
  'open_contact',
] as const;

export type AiToolName = (typeof AI_TOOL_NAMES)[number];

export const navigateToRoomArgsSchema = z
  .object({
    roomId: z.enum(ROOM_IDS),
  })
  .strict();

export const openProjectArgsSchema = z
  .object({
    projectId: z.string().min(1),
  })
  .strict();

export const showSkillArgsSchema = z
  .object({
    skillId: z.string().min(1),
  })
  .strict();

export const showArchitectureArgsSchema = z
  .object({
    architectureCaseId: z.string().min(1),
  })
  .strict();

export const emptyArgsSchema = z.object({}).strict();

export const aiToolCallSchema = z.discriminatedUnion('name', [
  z.object({ name: z.literal('navigate_to_room'), arguments: navigateToRoomArgsSchema }),
  z.object({ name: z.literal('open_project'), arguments: openProjectArgsSchema }),
  z.object({ name: z.literal('show_skill'), arguments: showSkillArgsSchema }),
  z.object({ name: z.literal('show_architecture'), arguments: showArchitectureArgsSchema }),
  z.object({ name: z.literal('open_resume'), arguments: emptyArgsSchema }),
  z.object({ name: z.literal('open_contact'), arguments: emptyArgsSchema }),
]);

export type AiToolCall = z.infer<typeof aiToolCallSchema>;

export const aiIntentionSchema = z
  .object({
    action: z.enum([
      'navigate',
      'open_project',
      'show_skill',
      'show_architecture',
      'open_resume',
      'open_contact',
    ]),
    target: z.string().min(1).optional(),
  })
  .strict();

export type AiIntention = z.infer<typeof aiIntentionSchema>;
