import { publicRuntimeConfig } from '@/app/config/appConfig';
import type { Locale } from '@/types/locale';

export type PageMeta = {
  title: string;
  description: string;
  canonicalPath: string;
  locale: Locale;
};

export function buildPageMeta(meta: PageMeta) {
  const canonical = new URL(meta.canonicalPath, publicRuntimeConfig.siteUrl).toString();
  return {
    title: meta.title,
    description: meta.description,
    canonical,
    openGraph: {
      title: meta.title,
      description: meta.description,
      url: canonical,
      siteName: 'Digital Residence',
      locale: meta.locale === 'zh-CN' ? 'zh_CN' : 'en_US',
    },
  };
}

export function applyDocumentMeta(meta: PageMeta): void {
  if (typeof document === 'undefined') {
    return;
  }
  const resolved = buildPageMeta(meta);
  document.title = resolved.title;
  upsertMeta('description', resolved.description);
  upsertLink('canonical', resolved.canonical);
  upsertMeta('og:title', resolved.openGraph.title, 'property');
  upsertMeta('og:description', resolved.openGraph.description, 'property');
  upsertMeta('og:url', resolved.openGraph.url, 'property');
  document.documentElement.lang = meta.locale;
}

function upsertMeta(name: string, content: string, attribute: 'name' | 'property' = 'name'): void {
  const selector = `meta[${attribute}="${name}"]`;
  let element = document.head.querySelector(selector);
  if (!element) {
    element = document.createElement('meta');
    element.setAttribute(attribute, name);
    document.head.append(element);
  }
  element.setAttribute('content', content);
}

function upsertLink(rel: string, href: string): void {
  let element = document.head.querySelector(`link[rel="${rel}"]`);
  if (!element) {
    element = document.createElement('link');
    element.setAttribute('rel', rel);
    document.head.append(element);
  }
  element.setAttribute('href', href);
}
