import { describe, expect, it } from 'vitest';

import { nextAssetState } from '@/assets/loaders/assetLifecycle';
import { searchCatalog } from '@/search/searchCatalog';
import { buildJsonLd } from '@/seo/jsonLd';
import { assertNoFrontendSecrets } from '@/security/env';

describe('asset lifecycle', () => {
  it('follows UNLOADED → QUEUED → LOADING → READY', () => {
    const queued = nextAssetState('UNLOADED', 'queue');
    const loading = nextAssetState(queued, 'start');
    const ready = nextAssetState(loading, 'succeed');
    expect(ready).toBe('READY');
  });

  it('can fail from LOADING', () => {
    expect(nextAssetState('LOADING', 'fail')).toBe('FAILED');
  });
});

describe('search and SEO gates', () => {
  it('indexes nothing from placeholder private content', () => {
    expect(searchCatalog('engineer', 'en')).toEqual([]);
  });

  it('does not emit Person JSON-LD for placeholder profiles', () => {
    const nodes = buildJsonLd('en');
    expect(nodes.some((node) => node['@type'] === 'Person')).toBe(false);
    expect(nodes.some((node) => node['@type'] === 'WebSite')).toBe(true);
  });
});

describe('frontend secret hygiene', () => {
  it('flags non-public secret-like keys', () => {
    expect(assertNoFrontendSecrets({ OPENAI_API_KEY: 'sk-test' })).toEqual(['OPENAI_API_KEY']);
    expect(assertNoFrontendSecrets({ VITE_PUBLIC_APP_NAME: 'Digital Residence' })).toEqual([]);
  });
});
