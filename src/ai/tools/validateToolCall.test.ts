import { describe, expect, it } from 'vitest';

import { validateIntention, validateToolCall } from '@/ai/tools/validateToolCall';
import { toolCallToCommand } from '@/ai/tools/toCommand';

describe('AI tool validation', () => {
  it('accepts an allowlisted navigation tool', () => {
    const result = validateToolCall({
      name: 'navigate_to_room',
      arguments: { roomId: 'ai-lab' },
    });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(toolCallToCommand(result.value)).toEqual({
        type: 'NAVIGATE_TO_ROOM',
        roomId: 'ai-lab',
        source: 'ai',
      });
    }
  });

  it('rejects unknown tools', () => {
    const result = validateToolCall({
      name: 'rm_rf',
      arguments: { path: '/' },
    });
    expect(result.ok).toBe(false);
  });

  it('rejects opening unpublished projects', () => {
    const result = validateToolCall({
      name: 'open_project',
      arguments: { projectId: 'does-not-exist' },
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe('PROJECT_NOT_INDEXABLE');
    }
  });

  it('rejects navigate intentions without a target', () => {
    const result = validateIntention({ action: 'navigate' });
    expect(result.ok).toBe(false);
  });

  it('accepts open_contact without a target', () => {
    const result = validateIntention({ action: 'open_contact' });
    expect(result.ok).toBe(true);
  });
});
