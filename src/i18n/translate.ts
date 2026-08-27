import { enMessages, type MessageTree } from '@/i18n/catalogs/en';
import { zhCNMessages } from '@/i18n/catalogs/zh-CN';
import { FALLBACK_LOCALE, type Locale } from '@/types/locale';

type DotPaths<T, Prefix extends string = ''> = T extends string
  ? Prefix
  : {
      [K in keyof T & string]: DotPaths<T[K], Prefix extends '' ? K : `${Prefix}.${K}`>;
    }[keyof T & string];

export type MessageKey = DotPaths<MessageTree>;

const catalogs: Record<Locale, MessageTree> = {
  en: enMessages,
  'zh-CN': zhCNMessages,
};

function readPath(tree: unknown, path: string): string | undefined {
  const segments = path.split('.');
  let cursor: unknown = tree;
  for (const segment of segments) {
    if (typeof cursor !== 'object' || cursor === null || !(segment in cursor)) {
      return undefined;
    }
    cursor = (cursor as Record<string, unknown>)[segment];
  }
  return typeof cursor === 'string' ? cursor : undefined;
}

export function translate(locale: Locale, key: MessageKey): string {
  const primary = readPath(catalogs[locale], key);
  if (primary) {
    return primary;
  }
  const fallback = readPath(catalogs[FALLBACK_LOCALE], key);
  if (fallback) {
    return fallback;
  }
  return key;
}

export function getCatalog(locale: Locale): MessageTree {
  return catalogs[locale] ?? catalogs[FALLBACK_LOCALE];
}
