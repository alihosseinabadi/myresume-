/** Canned demo content used by the AI panel when the API is unreachable. */

export type DemoMode = 'summary' | 'bullets' | 'skills'

export const DEMO_MODES: { id: DemoMode; label: string; icon: string; cta: string }[] = [
  { id: 'summary', label: 'Summary', icon: 'sparkle', cta: 'Write my summary' },
  { id: 'bullets', label: 'Bullets', icon: 'wand', cta: 'Generate achievements' },
  { id: 'skills', label: 'Skills', icon: 'library', cta: 'Suggest skills' },
]

export const DEMO_FALLBACK: Record<DemoMode, string[]> = {
  summary: [
    'Impact-driven Data Scientist specializing in the ML lifecycle and intelligent system development, with a portfolio of 10+ diverse ML & AI projects.',
    'Integrate local and cloud LLMs (Ollama, GigaChat, ChatGPT) to solve business problems, with prompt engineering and fine-tuning for better accuracy.',
    'Now targeting ML engineering roles where intelligent systems ship to production.',
  ],
  bullets: [
    'Applied ML and AI techniques for student performance tracking, driving 35% enrollment growth through data-driven insights.',
    'Built intelligent systems that turn business problems into actionable PDF reports, integrating Ollama, GigaChat and ChatGPT APIs.',
    'Managed multilingual content (Persian, Turkish, English) with AI-assisted content development and cross-cultural documentation.',
  ],
  skills: ['Python', 'Scikit-learn', 'Ollama', 'GigaChat', 'ChatGPT API', 'Pandas', 'NumPy', 'SQL', 'Prompt Engineering'],
}
