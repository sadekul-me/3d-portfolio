import type { AiChatRequest, AiChatResponse, AiClient } from '@/ai/contracts/chat';

/**
 * Placeholder client. The production implementation will live behind the same-origin API.
 * Browser code must never hold provider credentials.
 */
export class UnimplementedAiClient implements AiClient {
  chat(_request: AiChatRequest): Promise<AiChatResponse> {
    return Promise.reject(
      new Error('AI client is not implemented in the architecture foundation phase.'),
    );
  }
}
