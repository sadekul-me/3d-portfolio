/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_PUBLIC_APP_NAME?: string;
  readonly VITE_PUBLIC_APP_VERSION?: string;
  readonly VITE_PUBLIC_BUILD_ID?: string;
  readonly VITE_PUBLIC_SITE_URL?: string;
  readonly VITE_PUBLIC_API_BASE_URL?: string;
  readonly VITE_PUBLIC_ENABLE_DIAGNOSTICS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
