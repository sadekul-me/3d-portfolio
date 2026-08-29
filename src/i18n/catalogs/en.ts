export const enMessages = {
  app: {
    name: 'Digital Residence',
    skipToContent: 'Skip to content',
    skipCinematic: 'Skip cinematic',
    language: 'Language',
    english: 'English',
    chinese: '简体中文',
  },
  landing: {
    kicker: 'Interactive 3D portfolio',
    title: 'Digital Residence',
    subtitle:
      'A cinematic residence for software engineering, AI systems, and architectural thinking. The 3D world is an experience layer, never an information barrier.',
    enterExperience: 'Enter Experience',
    quickPortfolio: 'Quick Portfolio',
    resume: 'Resume',
    contact: 'Contact',
    soundOn: 'Sound on',
    soundOff: 'Sound off',
    placeholderNotice:
      'Canonical professional content has not been authored yet. This foundation exposes architecture, navigation, and access paths only.',
  },
  look: {
    label: 'Presentation',
    system: 'System',
    cinematic: 'Cinematic',
  },
  nav: {
    map: 'Residence map',
    currentLocation: 'Current location',
    visited: 'Visited',
    exterior: 'Exterior',
    identity: 'Identity',
    engineering: 'Engineering',
    aiLab: 'AI Lab',
    projects: 'Projects',
    architecture: 'Architecture',
    commandCenter: 'Command Center',
  },
  portfolio: {
    title: 'Quick Portfolio',
    intro:
      'All core professional information remains available without WebGL. This path is first-class, not a consolation route.',
    about: 'About',
    experience: 'Experience',
    skills: 'Skills',
    projects: 'Projects',
    architecture: 'Architecture',
    empty:
      'No published entries yet. Content will appear here from the same canonical catalog used by the 3D residence.',
  },
  experience: {
    loading: 'Preparing the residence',
    reduced: 'Reduced 3D mode',
    lightweight: 'Lightweight experience',
    webglUnavailable: 'WebGL is unavailable. Opening Quick Portfolio.',
  },
  contact: {
    title: 'Command Center',
    unavailable: 'The contact form will be available when canonical contact details are published.',
  },
  resume: {
    title: 'Resume',
    unavailable: 'A published resume is not available yet. The HTML representation will live here.',
  },
  errors: {
    generic: 'Something went wrong. Core portfolio information remains available.',
    navigationInvalid: 'That room is not available.',
    assetFailed: 'Part of the scene could not load. A simpler representation is being used.',
    aiUnavailable: 'The AI guide is unavailable. Search and navigation still work.',
  },
  a11y: {
    reducedMotion: 'Reduced motion is on. Cinematic travel is shortened.',
    primaryNav: 'Primary',
    experienceCanvas: 'Interactive 3D residence',
  },
  diagnostics: {
    title: 'Diagnostics',
    hidden: 'Diagnostics are not shown to visitors.',
  },
} as const;

type DeepString<T> = T extends string ? string : { [K in keyof T]: DeepString<T[K]> };

export type MessageTree = DeepString<typeof enMessages>;
