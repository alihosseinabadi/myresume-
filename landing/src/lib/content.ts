import type { Tool } from './types'

/** The nine-tool grid: "Everything you need to land interviews in one place". */
export const TOOLS: Tool[] = [
  {
    id: 'resume-builder',
    name: 'Resume Builder',
    description: 'Build a recruiter-ready CV in minutes with AI-assisted phrasing in every section.',
    icon: 'file',
  },
  {
    id: 'cover-letter',
    name: 'Cover Letter Builder',
    description: 'Generate a matching cover letter in a few clicks, tailored to the job ad.',
    icon: 'mail',
  },
  {
    id: 'resume-checker',
    name: 'Resume checker',
    description: 'Unlimited ATS reports with prioritised, personalised fixes before you apply.',
    icon: 'scan',
  },
  {
    id: 'resignation-letter',
    name: 'Resignation letter builder',
    description: 'Leave on good terms with a professionally worded resignation letter.',
    icon: 'pen',
  },
  {
    id: 'headshot-pro',
    name: 'Headshot pro',
    badge: 'Premium',
    description: 'Studio-quality AI headshots with three backdrops, delivered in about an hour.',
    icon: 'camera',
  },
  {
    id: 'career-test',
    name: 'Career test',
    description: 'Find the roles that match your strengths before you start applying.',
    icon: 'compass',
  },
  {
    id: 'job-search',
    name: 'Job search',
    badge: 'Premium',
    description: 'Search openings across major boards without leaving the builder.',
    icon: 'search',
  },
  {
    id: 'job-tracker',
    name: 'Job tracker',
    badge: 'Premium',
    description: 'Track every application, interview stage and follow-up in one board.',
    icon: 'kanban',
  },
  {
    id: 'remote-job',
    name: 'Remote job',
    description: 'Browse curated remote-first openings matched to the CV you just built.',
    icon: 'globe',
  },
]

/** "Create your CV in 4 steps". */
/**
 * Where each tool chip goes. Tools without an entry are not built yet — the
 * Toolkit says so instead of linking nowhere.
 */
export const TOOL_TARGETS: Record<string, string> = {
  'resume-builder': '#tool=cv',
  'cover-letter': '#tool=cover-letter',
  'resume-checker': '#tool=cv',
  'resignation-letter': '#tool=resignation',
  'career-test': '#tool=career-test',
}

export const PLANNED_NOTE =
  'Not built yet. Working now: the CV builder with ATS scoring, the cover letter and ' +
  'resignation letter writers, and the career test.'

/** The tab in the studio panel a tool opens. */
export const TOOL_TAB: Record<string, 'job' | 'letters' | 'style'> = {
  cv: 'job',
  'job-link': 'job',
  'cover-letter': 'letters',
  letters: 'letters',
  resignation: 'letters',
  'career-test': 'letters',
  style: 'style',
  templates: 'style',
}

/** Section ids that exist on the page, so every nav link has a target. */
export const SECTION_IDS = ['top', 'studio', 'toolkit', 'templates', 'pricing', 'faq'] as const

export const STEPS = [
  {
    n: '01',
    title: 'Start your way',
    body: 'Import an existing CV or start from scratch in the distraction-free editor.',
  },
  {
    n: '02',
    title: 'Write it with AI',
    body: 'Get tailored, recruiter-approved phrasing for every section as you type.',
  },
  {
    n: '03',
    title: 'Make it yours',
    body: 'Adjust colours, fonts and spacing in one click across 11 templates.',
  },
  {
    n: '04',
    title: 'Download and apply',
    body: 'Export to PDF or Word, ATS-safe, and start applying the same day.',
  },
]

/** "6 Reasons to Create Your CV with MyResume". */
export const REASONS = [
  {
    title: 'CV Creator',
    body: 'Build your CV online in a clean, distraction-free editor that autosaves every keystroke.',
    icon: 'sparkle',
  },
  {
    title: 'Pre-written content',
    body: 'Not sure what to write? Start from recruiter-validated content and edit it down.',
    icon: 'library',
  },
  {
    title: 'AI Assistant',
    body: 'Content suggestions for every section, written by AI and reviewed by recruiters.',
    icon: 'wand',
  },
  {
    title: 'Multilingual templates',
    body: 'Translate headings into 20+ languages in one click while keeping the layout intact.',
    icon: 'globe',
  },
  {
    title: 'Cover Letter Creator',
    body: 'Create a matching cover letter in just a few clicks using pre-written content.',
    icon: 'mail',
  },
  {
    title: 'Approved templates',
    body: 'Every template is recruiter-approved and optimised to pass ATS keyword scans.',
    icon: 'shield',
  },
]

/** Stat strip under the hero. */
export const STATS = [
  { value: '+1M', label: 'satisfied users' },
  { value: '11', label: 'recruiter-approved templates' },
  { value: '20+', label: 'languages supported' },
  { value: '4 min', label: 'median time to a finished CV' },
]
