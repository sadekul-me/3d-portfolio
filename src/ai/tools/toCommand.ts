import { isRoomId } from '@/types/ids';
import { asArchitectureCaseId, asProjectId, asSkillId } from '@/types/ids';
import type { AppCommand } from '@/app/commands/types';
import type { AiIntention, AiToolCall } from '@/ai/contracts/tools';

/**
 * AI output becomes an application command only after schema + policy validation.
 * The LLM never mutates React, Zustand, Three.js, or the filesystem.
 */
export function toolCallToCommand(call: AiToolCall): AppCommand {
  switch (call.name) {
    case 'navigate_to_room':
      return { type: 'NAVIGATE_TO_ROOM', roomId: call.arguments.roomId, source: 'ai' };
    case 'open_project':
      return {
        type: 'OPEN_PROJECT',
        projectId: asProjectId(call.arguments.projectId),
        source: 'ai',
      };
    case 'show_skill':
      return { type: 'SHOW_SKILL', skillId: asSkillId(call.arguments.skillId), source: 'ai' };
    case 'show_architecture':
      return {
        type: 'SHOW_ARCHITECTURE',
        architectureCaseId: asArchitectureCaseId(call.arguments.architectureCaseId),
        source: 'ai',
      };
    case 'open_resume':
      return { type: 'OPEN_RESUME', source: 'ai' };
    case 'open_contact':
      return { type: 'OPEN_CONTACT', source: 'ai' };
  }
}

export function intentionToCommand(intention: AiIntention): AppCommand | null {
  switch (intention.action) {
    case 'navigate':
      return intention.target && isRoomId(intention.target)
        ? { type: 'NAVIGATE_TO_ROOM', roomId: intention.target, source: 'ai' }
        : null;
    case 'open_project':
      return intention.target
        ? { type: 'OPEN_PROJECT', projectId: asProjectId(intention.target), source: 'ai' }
        : null;
    case 'show_skill':
      return intention.target
        ? { type: 'SHOW_SKILL', skillId: asSkillId(intention.target), source: 'ai' }
        : null;
    case 'show_architecture':
      return intention.target
        ? {
            type: 'SHOW_ARCHITECTURE',
            architectureCaseId: asArchitectureCaseId(intention.target),
            source: 'ai',
          }
        : null;
    case 'open_resume':
      return { type: 'OPEN_RESUME', source: 'ai' };
    case 'open_contact':
      return { type: 'OPEN_CONTACT', source: 'ai' };
    default:
      return null;
  }
}
