export const ERROR_CATEGORIES = [
  'APP',
  'SCENE',
  'ASSET',
  'RENDER',
  'NAVIGATION',
  'AI',
  'RETRIEVAL',
  'TOOL',
  'CONTACT',
  'I18N',
  'PERFORMANCE',
  'SECURITY',
  'RECOVERY',
] as const;

export type ErrorCategory = (typeof ERROR_CATEGORIES)[number];

export const ERROR_SEVERITIES = ['INFO', 'WARN', 'ERROR', 'CRITICAL'] as const;
export type ErrorSeverity = (typeof ERROR_SEVERITIES)[number];
