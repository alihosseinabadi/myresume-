export type Template = {
  id: string
  name: string
  accent: string
  tagline: string
  atsReady: boolean
  layout: 'sidebar' | 'single' | 'two-column'
}

export type Tool = {
  id: string
  name: string
  description: string
  badge?: 'Premium'
  icon: string
}
