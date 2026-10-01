/**
 * Typed client for the MyResume FastAPI backend.
 *
 * Every helper degrades gracefully: if the API is unreachable the landing page
 * still renders using the local sample resume, so a demo never shows an error.
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

export type PersonalInfo = {
  full_name: string
  headline: string
  email: string
  phone: string
  location: string
  website: string
  linkedin: string
  github: string
}

export type ExperienceItem = {
  id: string
  role: string
  company: string
  location: string
  start_date: string
  end_date: string
  current: boolean
  bullets: string[]
}

export type SkillGroup = { id: string; name: string; skills: string[] }

export type Resume = {
  id: string
  title: string
  template: string
  accent_color: string
  locale: string
  personal: PersonalInfo
  summary: string
  experience: ExperienceItem[]
  education: { id: string; degree: string; school: string; location: string }[]
  skills: SkillGroup[]
  languages: { id: string; name: string; level: string }[]
}

export type AiText = {
  text: string
  provider: string
  model: string
  latency_ms: number
  fallback: boolean
}

export type AiList = {
  items: string[]
  provider: string
  model: string
  latency_ms: number
  fallback: boolean
}

export type AtsCheck = {
  id: string
  label: string
  passed: boolean
  weight: number
  detail: string
}

export type AtsScore = {
  score: number
  grade: string
  matched_keywords: string[]
  missing_keywords: string[]
  checks: AtsCheck[]
  suggestions: string[]
}

export type Health = {
  status: string
  app: string
  ai_provider: string
  ai_ready: boolean
}

export type JobPosting = {
  url: string
  ok: boolean
  title: string
  company: string
  location: string
  description: string
  keywords: string[]
  source: string
  engine: string
  attempts: string[]
  message: string
}

export type TailorResult = {
  resume: Resume
  score: AtsScore
  job: JobPosting
  matched_keywords: string[]
  missing_keywords: string[]
  provider: string
  notes: string[]
}

export type TailorPayload = {
  url?: string
  job_description?: string
  job_title?: string
  locale?: string
  template?: string
  full_name?: string
  email?: string
  location?: string
  years_experience?: number
  seniority?: string
  tone?: string
  skills?: string[]
  achievements?: string[]
  base_resume?: Resume
}

export type Resignation = {
  letter: string
  provider: string
  fallback: boolean
  word_count: number
  checklist: string[]
}

export type CareerRole = {
  family: string
  field: string
  title: string
  why: string
}

export type CareerMatch = {
  roles: CareerRole[]
  skills: string[]
  note: string
}

const TIMEOUT_MS = 4000

/**
 * A POST asks the engine to *write* something, which takes far longer than a
 * probe: the offline engine needs ~4s for a full CV and a live model can take
 * much more. Reads stay snappy so the status pill still fails over quickly.
 */
const WORK_TIMEOUT_MS = 30000

async function request<T>(path: string, init?: RequestInit): Promise<T | null> {
  const work = (init?.method ?? 'GET').toUpperCase() === 'POST'
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), work ? WORK_TIMEOUT_MS : TIMEOUT_MS)
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
      cache: 'no-store',
    })
    if (!response.ok) return null
    return (await response.json()) as T
  } catch {
    return null
  } finally {
    clearTimeout(timer)
  }
}

export const api = {
  health: () => request<Health>('/api/health'),

  sampleResume: (locale = 'en', template = 'athens') =>
    request<Resume>(`/api/resumes/sample?locale=${locale}&template=${template}`),

  summary: (body: {
    job_title: string
    industry?: string
    seniority?: string
    years_experience?: number
    skills?: string[]
    achievements?: string[]
    tone?: string
    existing_text?: string
  }) => request<AiText>('/api/ai/summary', { method: 'POST', body: JSON.stringify(body) }),

  bullets: (body: { job_title: string; role?: string; count?: number; achievements?: string[] }) =>
    request<AiList>('/api/ai/bullets', { method: 'POST', body: JSON.stringify(body) }),

  skills: (body: { job_title: string; limit?: number; existing_skills?: string[] }) =>
    request<AiList>('/api/ai/skills', { method: 'POST', body: JSON.stringify(body) }),

  coverLetter: (body: {
    job_title: string
    company: string
    job_description?: string
    highlights?: string[]
    hiring_manager?: string
    years_experience?: number
    seniority?: string
  }) => request<AiText>('/api/ai/cover-letter', { method: 'POST', body: JSON.stringify(body) }),

  atsScore: (resume: Resume, job_description = '') =>
    request<AtsScore>('/api/ai/ats-score', {
      method: 'POST',
      body: JSON.stringify({ resume, job_description }),
    }),

  translate: (target_locale: string, headings: string[] = []) =>
    request<{ locale: string; headings: Record<string, string> }>('/api/ai/translate', {
      method: 'POST',
      body: JSON.stringify({ target_locale, headings }),
    }),

  /** Fetch a job advert URL and return the posting we could read. */
  importJob: (url: string) =>
    request<JobPosting>('/api/jobs/import', {
      method: 'POST',
      body: JSON.stringify({ url }),
    }),

  /** Job link (or advert text, or title) → a CV written for that job + its ATS score. */
  tailor: (payload: TailorPayload) =>
    request<TailorResult>('/api/jobs/tailor', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /** Short, professional resignation letter. */
  resignation: (payload: {
    full_name?: string
    job_title?: string
    company?: string
    manager_name?: string
    last_working_day?: string
    reason?: string
    highlight?: string
    tone?: string
  }) =>
    request<Resignation>('/api/ai/resignation', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /** Career test: suggest role families and the skills to put on a CV. */
  careerMatch: (payload: {
    strength: 'ideas' | 'data' | 'people' | 'operations'
    interests?: string
    years_experience?: number
    seniority?: string
  }) =>
    request<CareerMatch>('/api/careers/match', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}

/** Local fallback used when the backend is not running (e.g. static preview). */
export const FALLBACK_RESUME: Resume = {
  id: 'local-sample',
  title: 'Ali Hosseinabadi — sample',
  template: 'athens',
  accent_color: '#0F766E',
  locale: 'en',
  personal: {
    full_name: 'Ali Hosseinabadi',
    headline: 'Data Scientist | Machine Learning Engineer',
    email: 'Hosseinabadiia@gmail.com',
    phone: '+7 999 000 4136',
    location: 'Moscow, Russia',
    website: '',
    linkedin: 'linkedin.com/in/ali-hosseinabadi',
    github: 'github.com/alihosseinabadi',
  },
  summary:
    'Impact-driven Data Scientist specializing in the machine learning lifecycle and intelligent system development. Portfolio of 10+ diverse ML & AI projects — LLM API integration (Ollama, GigaChat, ChatGPT), prompt engineering with fine-tuning, and end-to-end ML solutions. Formal training from School 21 (Ecole 42).',
  experience: [
    {
      id: 'e1',
      role: 'Technical Analyst & Consultant',
      company: 'PASSYOS Education Center',
      location: 'Moscow, Russia',
      start_date: '2022-01',
      end_date: '2024-12',
      current: false,
      bullets: [
        'Applied ML and AI techniques for student performance tracking, driving 35% enrollment growth through data-driven insights.',
        'Built intelligent systems that turn business problems into actionable reports in PDF format.',
        'Integrated local and cloud LLMs (Ollama, GigaChat, ChatGPT) to solve business problems with prompt engineering and fine-tuning.',
      ],
    },
    {
      id: 'e2',
      role: 'Content Creator & Consultant',
      company: 'PASSYOS Company',
      location: 'Istanbul, Turkey',
      start_date: '2020-01',
      end_date: '2022-12',
      current: false,
      bullets: [
        'Managed multilingual content across Persian, Turkish and English with AI-assisted content development.',
        'Produced cross-cultural training materials and technical documentation.',
      ],
    },
  ],
  education: [
    {
      id: 'ed1',
      degree: 'Data Scientist Track',
      school: 'School 21 Moscow (Ecole 42)',
      location: 'Moscow, Russia',
    },
    {
      id: 'ed2',
      degree: 'Information Technology & Informatics',
      school: 'RUDN University',
      location: 'Moscow, Russia',
    },
    {
      id: 'ed3',
      degree: 'Software Engineering',
      school: 'Istinye University',
      location: 'Istanbul, Turkey',
    },
  ],
  skills: [
    { id: 's1', name: 'ML & AI', skills: ['Scikit-learn', 'Classification', 'Regression', 'Clustering', 'Predictive Modeling'] },
    { id: 's2', name: 'LLMs', skills: ['Ollama', 'GigaChat', 'ChatGPT API', 'Prompt Engineering', 'Fine-tuning'] },
    { id: 's3', name: 'Programming & Data', skills: ['Python', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'C++', 'SQL'] },
    { id: 's4', name: 'Tools', skills: ['Git', 'GitLab', 'Linux', 'Bash', 'Power BI', 'Jupyter'] },
  ],
  languages: [
    { id: 'l1', name: 'Persian', level: 'C2' },
    { id: 'l2', name: 'English', level: 'C1' },
    { id: 'l3', name: 'Turkish', level: 'B1' },
    { id: 'l4', name: 'Russian', level: 'B1' },
    { id: 'l5', name: 'Arabic', level: 'A2' },
  ],
}
