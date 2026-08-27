/**
 * Custom GLSL is permitted only for signature visual effects or justified post-processing.
 * Standard materials are the default.
 */
export type ShaderPurpose = 'signature-effect' | 'post-processing';

export type ShaderRegistration = {
  id: string;
  purpose: ShaderPurpose;
  justification: string;
};

export const shaderRegistry: ShaderRegistration[] = [];
