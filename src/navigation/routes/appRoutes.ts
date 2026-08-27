export const APP_ROUTE_PATHS = {
  landing: '/',
  experience: '/experience',
  experienceRoom: '/experience/:roomId',
  portfolio: '/portfolio',
  portfolioAbout: '/portfolio/about',
  portfolioExperience: '/portfolio/experience',
  portfolioSkills: '/portfolio/skills',
  portfolioProjects: '/portfolio/projects',
  portfolioProject: '/portfolio/projects/:slug',
  portfolioArchitecture: '/portfolio/architecture',
  resume: '/resume',
  contact: '/contact',
} as const;

export type AppRouteName = keyof typeof APP_ROUTE_PATHS;

export function experienceRoomPath(roomId: string): string {
  return `/experience/${roomId}`;
}

export function projectPath(slug: string): string {
  return `/portfolio/projects/${slug}`;
}
