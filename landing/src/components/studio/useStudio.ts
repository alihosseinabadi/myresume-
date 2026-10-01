'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { API_BASE, FALLBACK_RESUME, api, type Resume } from '@/lib/api'
import { TEMPLATES } from '@/lib/templates'
import type { DemoMode } from '@/lib/demo'
import type { ShareBrief } from '@/lib/share'

/**
 * All state and side-effects behind the Studio panel.
 *
 * An optional `brief` (from a shared `/c/<payload>` link) only seeds the initial
 * template and language — everything stays editable afterwards.
 */
export function useStudio(brief?: ShareBrief) {
  const [jobTitle, setJobTitle] = useState(brief?.role || 'Data Analyst')
  const [templateId, setTemplateId] = useState(brief?.template || 'athens')
  const [locale, setLocale] = useState(brief?.locale || 'en')
  const [mode, setMode] = useState<DemoMode>('summary')
  const [lines, setLines] = useState<string[]>([])
  const [provider, setProvider] = useState('local')
  const [busy, setBusy] = useState(false)
  const [resume, setResume] = useState<Resume>(FALLBACK_RESUME)
  const [headings, setHeadings] = useState<Record<string, string>>({})
  const [online, setOnline] = useState<boolean | null>(null)
  const [exporting, setExporting] = useState('')
  const [notice, setNotice] = useState('')
  const [tailored, setTailored] = useState<Resume | null>(null)

  const template = useMemo(
    () => TEMPLATES.find((item) => item.id === templateId) ?? TEMPLATES[0],
    [templateId],
  )
  // Once a job has been tailored, the paper shows that CV instead of the sample.
  const preview: Resume = useMemo(
    () => ({ ...(tailored ?? resume), accent_color: template.accent, template: template.id }),
    [tailored, resume, template],
  )

  // The paper shows real backend content, not a hard-coded mock.
  useEffect(() => {
    let alive = true
    api.sampleResume(locale, templateId).then((result) => {
      if (!alive) return
      setOnline(Boolean(result))
      if (result) setResume(result)
    })
    return () => {
      alive = false
    }
  }, [locale, templateId])

  // Headings come from the deterministic translation table (no provider needed).
  useEffect(() => {
    if (locale === 'en') {
      setHeadings({})
      return
    }
    let alive = true
    api.translate(locale, ['Summary', 'Experience', 'Education', 'Skills']).then((result) => {
      if (alive && result) setHeadings(result.headings)
    })
    return () => {
      alive = false
    }
  }, [locale])

  const generate = useCallback(
    async (next: DemoMode) => {
      setMode(next)
      setBusy(true)
      setNotice('')
      try {
        if (next === 'summary') {
          const result = await api.summary({
            job_title: jobTitle,
            tone: 'confident',
            years_experience: 6,
          })
          setLines(result?.text ? [result.text] : [])
          setProvider(result?.provider ?? 'preview')
        } else if (next === 'bullets') {
          const result = await api.bullets({ job_title: jobTitle, count: 4 })
          setLines(result?.items ?? [])
          setProvider(result?.provider ?? 'preview')
        } else {
          const result = await api.skills({ job_title: jobTitle, limit: 10 })
          setLines(result?.items ?? [])
          setProvider(result?.provider ?? 'preview')
        }
        if (!lines.length) setNotice('Start the API to generate live output.')
      } finally {
        setBusy(false)
      }
    },
    [jobTitle, lines.length],
  )

  const exportAs = useCallback(
    async (format: 'pdf' | 'docx' | 'txt') => {
      setExporting(format)
      setNotice('')
      try {
        const response = await fetch(`${API_BASE}/api/export/${format}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(preview),
        })
        if (!response.ok) throw new Error('export failed')
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const disposition = response.headers.get('Content-Disposition') ?? ''
        const link = document.createElement('a')
        link.href = url
        link.download = disposition.match(/filename="(.+?)"/)?.[1] ?? `myresume.${format}`
        document.body.appendChild(link)
        link.click()
        link.remove()
        URL.revokeObjectURL(url)
      } catch {
        setNotice(`Export needs the API running on ${API_BASE}.`)
      } finally {
        setExporting('')
      }
    },
    [preview],
  )

  return {
    jobTitle, setJobTitle, templateId, setTemplateId, locale, setLocale,
    mode, lines, provider, busy, headings, online, exporting, notice, preview, template,
    generate, exportAs, tailored, setTailored,
  }
}
