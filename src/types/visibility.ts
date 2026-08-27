export const PUBLICATION_STATUSES = ['placeholder', 'draft', 'published'] as const;
export type PublicationStatus = (typeof PUBLICATION_STATUSES)[number];

/**
 * Visibility is a capability set, not a single flag.
 * AI indexing may only consume records that are both published and aiReadable.
 */
export type ContentVisibility = {
  public: boolean;
  aiReadable: boolean;
  searchable: boolean;
  internal: boolean;
};

export const PRIVATE_VISIBILITY: ContentVisibility = {
  public: false,
  aiReadable: false,
  searchable: false,
  internal: true,
};

export const PUBLIC_VISIBILITY: ContentVisibility = {
  public: true,
  aiReadable: true,
  searchable: true,
  internal: false,
};

export function isAiIndexable(
  visibility: ContentVisibility,
  publicationStatus: PublicationStatus,
): boolean {
  return publicationStatus === 'published' && visibility.aiReadable && !visibility.internal;
}

export function isSearchIndexable(
  visibility: ContentVisibility,
  publicationStatus: PublicationStatus,
): boolean {
  return publicationStatus === 'published' && visibility.searchable && !visibility.internal;
}

export function isPubliclyListed(
  visibility: ContentVisibility,
  publicationStatus: PublicationStatus,
): boolean {
  return publicationStatus === 'published' && visibility.public && !visibility.internal;
}
