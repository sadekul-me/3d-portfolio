export type SpatialUiConstraint = {
  maxCharactersComfortable: number;
  allowWrap: boolean;
};

/**
 * Spatial labels must survive English and Simplified Chinese length differences.
 */
export const spatialUiConstraints: Record<'label' | 'title' | 'body', SpatialUiConstraint> = {
  label: { maxCharactersComfortable: 24, allowWrap: false },
  title: { maxCharactersComfortable: 48, allowWrap: true },
  body: { maxCharactersComfortable: 140, allowWrap: true },
};
