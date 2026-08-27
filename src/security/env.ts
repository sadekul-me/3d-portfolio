const PUBLIC_PREFIX = 'VITE_PUBLIC_';

/**
 * Frontend code may only read public-prefixed env vars.
 * Presence of a secret-like key in import.meta.env should fail audits.
 */
export function assertNoFrontendSecrets(env: Record<string, string | undefined>): string[] {
  const suspicious = [
    'SECRET',
    'PRIVATE_KEY',
    'SMTP',
    'OPENAI',
    'ANTHROPIC',
    'DATABASE',
    'PASSWORD',
  ];
  const violations: string[] = [];
  for (const [key, value] of Object.entries(env)) {
    if (!value) {
      continue;
    }
    if (
      suspicious.some((token) => key.toUpperCase().includes(token)) &&
      !key.startsWith(PUBLIC_PREFIX)
    ) {
      violations.push(key);
    }
  }
  return violations;
}
