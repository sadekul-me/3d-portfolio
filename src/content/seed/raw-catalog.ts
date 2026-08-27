import type { RawCatalog } from '@/content/schemas/catalog';
import { PRIVATE_VISIBILITY } from '@/types/visibility';

const placeholderHeadline = {
  en: '[PLACEHOLDER] Software Engineer · AI Systems Builder · Product Architect',
  'zh-CN': '[PLACEHOLDER] 软件工程师 · AI 系统构建者 · 产品架构师',
} as const;

const placeholderSummary = {
  en: '[PLACEHOLDER] Canonical professional facts have not been authored yet. This record exists so the content pipeline, visibility rules, and Quick Portfolio shell can be verified without inventing a biography.',
  'zh-CN':
    '[PLACEHOLDER] 正式职业事实尚未写入。该记录仅用于验证内容管线、可见性规则和 Quick Portfolio 骨架，不构成个人履历声明。',
} as const;

/**
 * Production seed. Rooms are real product zones.
 * Profile and professional entities are explicitly placeholder — do not treat them as claims.
 */
export const rawCatalog: RawCatalog = {
  version: '0.1.0-foundation',
  profile: {
    id: 'owner',
    publicationStatus: 'placeholder',
    displayName: '[PLACEHOLDER] Portfolio Owner',
    headline: placeholderHeadline,
    summary: placeholderSummary,
    focusAreas: [
      {
        en: '[PLACEHOLDER] Software engineering',
        'zh-CN': '[PLACEHOLDER] 软件工程',
      },
      {
        en: '[PLACEHOLDER] AI systems',
        'zh-CN': '[PLACEHOLDER] AI 系统',
      },
      {
        en: '[PLACEHOLDER] System architecture',
        'zh-CN': '[PLACEHOLDER] 系统架构',
      },
    ],
    professionalLinks: [],
    visibility: PRIVATE_VISIBILITY,
  },
  rooms: [
    {
      id: 'exterior',
      route: '/experience/exterior',
      title: { en: 'Exterior', 'zh-CN': '外观' },
      purpose: {
        en: 'Cinematic arrival and first impression of the digital residence.',
        'zh-CN': '数字居所的电影化抵达与第一印象。',
      },
      preloadPriority: 'critical',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['identity'],
      assetManifestId: 'room-exterior',
      capabilities: ['cinematic-intro', 'guided-navigation', 'audio'],
      fallbackMode: 'LIGHTWEIGHT',
      sceneModule: '@/scenes/exterior/definition',
    },
    {
      id: 'identity',
      route: '/experience/identity',
      title: { en: 'Identity Atrium', 'zh-CN': '身份中庭' },
      purpose: {
        en: 'Who this engineer is, what they build, and how to read the residence.',
        'zh-CN': '工程师是谁、构建什么，以及如何阅读这座居所。',
      },
      preloadPriority: 'critical',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['exterior', 'engineering', 'projects', 'command-center'],
      assetManifestId: 'room-identity',
      capabilities: ['spatial-ui', 'guided-navigation', 'identity-timeline'],
      fallbackMode: 'QUICK_PORTFOLIO',
      sceneModule: '@/scenes/identity/definition',
    },
    {
      id: 'engineering',
      route: '/experience/engineering',
      title: { en: 'Engineering Chamber', 'zh-CN': '工程厅' },
      purpose: {
        en: 'Skills connected to projects, experience, and architectural evidence.',
        'zh-CN': '与项目、经历和架构证据相连的技能。',
      },
      preloadPriority: 'high',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['identity', 'ai-lab', 'projects', 'architecture'],
      assetManifestId: 'room-engineering',
      capabilities: ['spatial-ui', 'skill-evidence', 'guided-navigation'],
      fallbackMode: 'QUICK_PORTFOLIO',
      sceneModule: '@/scenes/engineering/definition',
    },
    {
      id: 'ai-lab',
      route: '/experience/ai-lab',
      title: { en: 'AI Lab', 'zh-CN': 'AI 实验室' },
      purpose: {
        en: 'Grounded intelligence layer: retrieval, tools, safety, and observability.',
        'zh-CN': '有依据的智能层：检索、工具、安全与可观测性。',
      },
      preloadPriority: 'high',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['engineering', 'architecture', 'command-center'],
      assetManifestId: 'room-ai-lab',
      capabilities: ['ai-visualization', 'spatial-ui', 'guided-navigation'],
      fallbackMode: 'LIGHTWEIGHT',
      sceneModule: '@/scenes/ai-lab/definition',
    },
    {
      id: 'projects',
      route: '/experience/projects',
      title: { en: 'Project Gallery', 'zh-CN': '项目展廊' },
      purpose: {
        en: 'Case studies covering problem, role, implementation, and outcomes.',
        'zh-CN': '涵盖问题、角色、实现与结果的案例。',
      },
      preloadPriority: 'high',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['identity', 'engineering', 'architecture', 'command-center'],
      assetManifestId: 'room-projects',
      capabilities: ['project-media', 'spatial-ui', 'guided-navigation'],
      fallbackMode: 'QUICK_PORTFOLIO',
      sceneModule: '@/scenes/projects/definition',
    },
    {
      id: 'architecture',
      route: '/experience/architecture',
      title: { en: 'Architecture Zone', 'zh-CN': '架构区' },
      purpose: {
        en: 'Interactive system design: nodes, flows, decisions, and trade-offs.',
        'zh-CN': '交互式系统设计：节点、流向、决策与权衡。',
      },
      preloadPriority: 'normal',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['engineering', 'ai-lab', 'projects'],
      assetManifestId: 'room-architecture',
      capabilities: ['architecture-graph', 'spatial-ui', 'guided-navigation'],
      fallbackMode: 'QUICK_PORTFOLIO',
      sceneModule: '@/scenes/architecture/definition',
    },
    {
      id: 'command-center',
      route: '/experience/command-center',
      title: { en: 'Command Center', 'zh-CN': '指挥中心' },
      purpose: {
        en: 'Resume, professional links, and contact — the conversion climax.',
        'zh-CN': '简历、职业链接与联系方式，作为转化高潮。',
      },
      preloadPriority: 'high',
      qualityCompatibility: ['AUTO', 'HIGH', 'BALANCED', 'LOW'],
      adjacentRoomIds: ['identity', 'projects', 'ai-lab', 'exterior'],
      assetManifestId: 'room-command-center',
      capabilities: ['contact', 'spatial-ui', 'guided-navigation'],
      fallbackMode: 'QUICK_PORTFOLIO',
      sceneModule: '@/scenes/command-center/definition',
    },
  ],
  skills: [],
  experiences: [],
  education: [],
  achievements: [],
  projects: [],
  architectureCases: [],
  tags: [],
  mediaAssets: [],
  sceneBindings: [],
};
