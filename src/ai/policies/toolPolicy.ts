import { AI_TOOL_NAMES, type AiToolName } from '@/ai/contracts/tools';

export type ToolPolicyDecision = {
  allowed: boolean;
  reason?: string;
};

const ALLOWLIST = new Set<AiToolName>(AI_TOOL_NAMES);

/**
 * The model cannot execute arbitrary tools, filesystem, or browser runtime commands.
 */
export function authorizeTool(name: string): ToolPolicyDecision {
  if (!ALLOWLIST.has(name as AiToolName)) {
    return { allowed: false, reason: 'TOOL_NOT_ALLOWLISTED' };
  }
  return { allowed: true };
}

export function authorizeIntentionTarget(
  action: string,
  target: string | undefined,
): ToolPolicyDecision {
  if ((action === 'open_resume' || action === 'open_contact') && target) {
    return { allowed: false, reason: 'UNEXPECTED_TARGET' };
  }
  if (
    (action === 'navigate' ||
      action === 'open_project' ||
      action === 'show_skill' ||
      action === 'show_architecture') &&
    !target
  ) {
    return { allowed: false, reason: 'MISSING_TARGET' };
  }
  return { allowed: true };
}
