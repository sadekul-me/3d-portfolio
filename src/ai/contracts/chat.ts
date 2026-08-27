import { z } from 'zod';

import { localeSchema } from '@/content/schemas/common';

export const aiChatRequestSchema = z
  .object({
    message: z.string().min(1).max(4000),
    locale: localeSchema,
    sessionId: z.string().min(1),
    roomId: z.string().optional(),
    projectId: z.string().optional(),
  })
  .strict();

export const aiChatResponseSchema = z
  .object({
    answer: z.string(),
    actions: z.array(
      z
        .object({
          type: z.enum([
            'navigate',
            'open_project',
            'show_skill',
            'show_architecture',
            'open_resume',
            'open_contact',
          ]),
          target: z.string().optional(),
        })
        .strict(),
    ),
    sources: z.array(z.string()),
    requestId: z.string().min(1),
  })
  .strict();

export type AiChatRequest = z.infer<typeof aiChatRequestSchema>;
export type AiChatResponse = z.infer<typeof aiChatResponseSchema>;

export interface AiClient {
  chat(request: AiChatRequest): Promise<AiChatResponse>;
}
