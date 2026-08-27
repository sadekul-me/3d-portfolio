import { authorizeIntentionTarget, authorizeTool } from '@/ai/policies/toolPolicy';
import {
  aiIntentionSchema,
  aiToolCallSchema,
  type AiIntention,
  type AiToolCall,
} from '@/ai/contracts/tools';
import { getAiIndexableEntities, loadCatalog } from '@/content/repositories/catalogRepository';
import { isRoomId } from '@/types/ids';
import { err, ok, type Result } from '@/lib/result';

export type ToolValidationIssue = {
  code: string;
  message: string;
};

export function validateToolCall(input: unknown): Result<AiToolCall, ToolValidationIssue> {
  const parsed = aiToolCallSchema.safeParse(input);
  if (!parsed.success) {
    return err({
      code: 'SCHEMA_INVALID',
      message: parsed.error.issues[0]?.message ?? 'Invalid tool call',
    });
  }

  const policy = authorizeTool(parsed.data.name);
  if (!policy.allowed) {
    return err({ code: policy.reason ?? 'POLICY_DENIED', message: 'Tool is not permitted' });
  }

  return validateToolTarget(parsed.data);
}

export function validateIntention(input: unknown): Result<AiIntention, ToolValidationIssue> {
  const parsed = aiIntentionSchema.safeParse(input);
  if (!parsed.success) {
    return err({
      code: 'SCHEMA_INVALID',
      message: parsed.error.issues[0]?.message ?? 'Invalid intention',
    });
  }

  const policy = authorizeIntentionTarget(parsed.data.action, parsed.data.target);
  if (!policy.allowed) {
    return err({ code: policy.reason ?? 'POLICY_DENIED', message: 'Intention is not permitted' });
  }

  return ok(parsed.data);
}

function validateToolTarget(call: AiToolCall): Result<AiToolCall, ToolValidationIssue> {
  const catalog = loadCatalog();
  const indexable = getAiIndexableEntities(catalog);

  switch (call.name) {
    case 'navigate_to_room': {
      if (!isRoomId(call.arguments.roomId)) {
        return err({ code: 'UNKNOWN_ROOM', message: 'Room does not exist' });
      }
      return ok(call);
    }
    case 'open_project': {
      const project = catalog.projects.find((item) => item.id === call.arguments.projectId);
      if (!project || !indexable.projects.some((item) => item.id === project.id)) {
        return err({
          code: 'PROJECT_NOT_INDEXABLE',
          message: 'Project is not available to AI tools',
        });
      }
      return ok(call);
    }
    case 'show_skill': {
      const skill = catalog.skills.find((item) => item.id === call.arguments.skillId);
      if (!skill || !indexable.skills.some((item) => item.id === skill.id)) {
        return err({ code: 'SKILL_NOT_INDEXABLE', message: 'Skill is not available to AI tools' });
      }
      return ok(call);
    }
    case 'show_architecture': {
      const architectureCase = catalog.architectureCases.find(
        (item) => item.id === call.arguments.architectureCaseId,
      );
      if (
        !architectureCase ||
        !indexable.architectureCases.some((item) => item.id === architectureCase.id)
      ) {
        return err({
          code: 'ARCHITECTURE_NOT_INDEXABLE',
          message: 'Architecture case is not available to AI tools',
        });
      }
      return ok(call);
    }
    case 'open_resume':
    case 'open_contact':
      return ok(call);
    default: {
      return err({ code: 'UNKNOWN_TOOL', message: 'Unsupported tool' });
    }
  }
}
