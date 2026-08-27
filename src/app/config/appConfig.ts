import { z } from 'zod';

const publicEnvSchema = z.object({
  appName: z.string().min(1).default('Digital Residence'),
  appVersion: z.string().min(1).default('0.1.0'),
  buildId: z.string().min(1).default('local-dev'),
  siteUrl: z.string().url().default('http://localhost:5173'),
  apiBaseUrl: z.string().min(1).default('/api/v1'),
  enableDiagnostics: z.boolean().default(false),
  assetManifestVersion: z.string().min(1).default('0.1.0'),
});

function readPublicEnv() {
  const diagnosticsRaw = import.meta.env.VITE_PUBLIC_ENABLE_DIAGNOSTICS;
  return publicEnvSchema.parse({
    appName: import.meta.env.VITE_PUBLIC_APP_NAME ?? 'Digital Residence',
    appVersion: import.meta.env.VITE_PUBLIC_APP_VERSION ?? '0.1.0',
    buildId: import.meta.env.VITE_PUBLIC_BUILD_ID ?? 'local-dev',
    siteUrl: import.meta.env.VITE_PUBLIC_SITE_URL ?? 'http://localhost:5173',
    apiBaseUrl: import.meta.env.VITE_PUBLIC_API_BASE_URL ?? '/api/v1',
    enableDiagnostics: diagnosticsRaw === 'true',
    assetManifestVersion: '0.1.0',
  });
}

export const publicRuntimeConfig = readPublicEnv();

export type PublicRuntimeConfig = typeof publicRuntimeConfig;
