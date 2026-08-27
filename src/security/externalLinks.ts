export function externalLinkRel(rel?: 'me' | 'nofollow'): string {
  const extras = rel ? `${rel} ` : '';
  return `${extras}noopener noreferrer`.trim();
}

export function isSafeHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' || url.protocol === 'http:';
  } catch {
    return false;
  }
}
