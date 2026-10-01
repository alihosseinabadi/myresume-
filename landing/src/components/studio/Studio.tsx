'use client'

import { useEffect, useState } from 'react'
import Icon from '@/components/shared/Icon'
import PaperCard from '@/components/studio/PaperCard'
import JobToCv from '@/components/studio/JobToCv'
import LettersPanel from '@/components/studio/LettersPanel'
import StylePanel from '@/components/studio/StylePanel'
import { useStudio } from '@/components/studio/useStudio'
import { TOOL_TAB } from '@/lib/content'
import type { ShareBrief } from '@/lib/share'

type Tab = 'job' | 'letters' | 'style'

const TABS: { id: Tab; label: string; hint: string }[] = [
  { id: 'job', label: 'Job → CV', hint: 'paste a link' },
  { id: 'letters', label: 'Letters & test', hint: 'cover · resignation · career' },
  { id: 'style', label: 'Style & export', hint: '11 templates · 24 locales' },
]

/**
 * Three tabs, one panel, one live CV sheet.
 * Deep links: `#tool=cv | cover-letter | resignation | career-test | style`
 * (the toolkit chips and the template rail use these).
 *
 * Pass a `brief` when the visitor arrived through a shared `/c/<link>`: the job,
 * template and language are then pre-filled instead of starting from scratch.
 */
export default function Studio({ brief }: { brief?: ShareBrief } = {}) {
  const [tab, setTab] = useState<Tab>('job')
  const s = useStudio(brief)

  useEffect(() => {
    const apply = () => {
      const hash = window.location.hash.slice(1)
      if (hash.startsWith('tool=')) {
        const tool = hash.slice(5)
        const next = TOOL_TAB[tool]
        if (next) {
          setTab(next)
          document.getElementById('studio')?.scrollIntoView({ block: 'start' })
        }
        return
      }
      if (['studio', 'toolkit', 'templates', 'pricing', 'faq', 'top'].includes(hash)) {
        document.getElementById(hash)?.scrollIntoView({ block: 'start' })
      }
    }
    apply()
    window.addEventListener('hashchange', apply)
    return () => window.removeEventListener('hashchange', apply)
  }, [])

  return (
    <div id="studio" className="scroll-mt-20">
      <div className="panel overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3 sm:px-5">
          <div className="flex flex-wrap gap-2">
            {TABS.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setTab(item.id)}
                aria-pressed={tab === item.id}
                className={`rounded-pill px-4 py-2 text-sm font-bold transition ${
                  tab === item.id
                    ? 'btn-primary'
                    : 'border border-line text-dim hover:border-pop/50 hover:text-text'
                }`}
              >
                {item.label}
                <span
                  className={`ml-2 hidden font-mono text-[10px] uppercase tracking-wider sm:inline ${
                    tab === item.id ? 'text-white/70' : 'text-dimmer'
                  }`}
                >
                  {item.hint}
                </span>
              </button>
            ))}
          </div>
          <span className="inline-flex items-center gap-2 font-mono text-[11px] text-dimmer">
            <span
              className={`h-1.5 w-1.5 rounded-full ${s.online ? 'bg-mint' : 'bg-dimmer'}`}
              aria-hidden="true"
            />
            {s.online === null ? 'connecting…' : s.online ? 'engine online' : 'offline mode'}
          </span>
        </div>

        <div className="grid gap-6 p-4 sm:p-5 lg:grid-cols-[1.15fr_0.85fr] lg:gap-7">
          <div className="min-w-0">
            {tab === 'job' && (
              <JobToCv
                brief={brief}
                onResume={s.setTailored}
                template={s.template.id}
                locale={s.locale}
              />
            )}
            {tab === 'letters' && <LettersPanel />}
            {tab === 'style' && (
              <StylePanel
                templateId={s.templateId}
                setTemplateId={s.setTemplateId}
                locale={s.locale}
                setLocale={s.setLocale}
                headings={s.headings}
              />
            )}
          </div>

          <div className="min-w-0">
            <div className="flex items-center justify-between gap-2 pb-3">
              <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-dimmer">
                {s.tailored ? 'your tailored CV' : 'sample CV'} · {s.template.name} · {s.locale}
              </span>
              <div className="flex gap-1.5">
                {(['pdf', 'docx', 'txt'] as const).map((format) => (
                  <button
                    key={format}
                    type="button"
                    onClick={() => s.exportAs(format)}
                    disabled={s.exporting === format}
                    title={s.online ? `Download ${format.toUpperCase()}` : 'Start the API to export'}
                    className="inline-flex items-center gap-1 rounded-lg border border-line px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-wider text-dim transition hover:border-pop hover:text-pop disabled:opacity-40"
                  >
                    <Icon name="download" className="h-3 w-3" />
                    {s.exporting === format ? '…' : format}
                  </button>
                ))}
              </div>
            </div>
            <PaperCard resume={s.preview} />
            {s.notice && <p className="mt-3 font-mono text-[11px] text-rose">{s.notice}</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
