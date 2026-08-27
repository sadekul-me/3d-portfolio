export const API_PATHS = {
  aiChat: '/api/v1/ai/chat',
  contact: '/api/v1/contact',
  analyticsEvents: '/api/v1/analytics/events',
  publicConfig: '/api/v1/config/public',
  healthLive: '/api/v1/health/live',
  healthReady: '/api/v1/health/ready',
} as const;

export type ApiPath = (typeof API_PATHS)[keyof typeof API_PATHS];
