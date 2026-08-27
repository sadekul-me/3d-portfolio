import { isPubliclyListed } from '@/types/visibility';
import { localizedValue, type Locale } from '@/types/locale';
import { loadCatalog } from '@/content/repositories/catalogRepository';
import { publicRuntimeConfig } from '@/app/config/appConfig';

export type JsonLdNode = Record<string, unknown>;

/**
 * Emit JSON-LD only for published public content.
 * Placeholder biographies must not become Person claims.
 */
export function buildJsonLd(locale: Locale, catalog = loadCatalog()): JsonLdNode[] {
  const nodes: JsonLdNode[] = [
    {
      '@type': 'WebSite',
      name: 'Digital Residence',
      url: publicRuntimeConfig.siteUrl,
      inLanguage: locale,
    },
  ];

  if (isPubliclyListed(catalog.profile.visibility, catalog.profile.publicationStatus)) {
    nodes.push({
      '@type': 'Person',
      name: catalog.profile.displayName,
      description: localizedValue(catalog.profile.summary, locale),
      url: publicRuntimeConfig.siteUrl,
    });
    nodes.push({
      '@type': 'ProfilePage',
      name: catalog.profile.displayName,
      url: `${publicRuntimeConfig.siteUrl}/portfolio/about`,
    });
  }

  return nodes;
}

export function toJsonLdScript(nodes: JsonLdNode[]): string {
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@graph': nodes,
  });
}
