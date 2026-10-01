'use client'

import { useState } from 'react'
import Icon from '@/components/shared/Icon'
import ResignationForm from '@/components/studio/ResignationForm'
import CareerTest from '@/components/studio/CareerTest'
import { api } from '@/lib/api'

type Mode = 'cover' | 'resignation'

const MODES: { id: Mode; label: string; icon: string }[] = [
  { id: 'cover', label: 'Cover letter', icon: 'mail' },
  { id: 'resignation', label: 'Resignation', icon: 'pen' },
]

const input =
  'w-full rounded-xl border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text outline-none transition placeholder:text-dimmer focus:border-pop'
const label = 'block text-xs font-semibold uppercase tracking-wider text-dimmer'

/** Real letter writers, so those tool chips land on something that works. */
export default function LettersPanel() {
  const [mode, setMode] = useState<Mode>('cover')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [cover, setCover] = useState('')

  const [company, setCompany] = useState('Payflow')
  const [jobTitle, setJobTitle] = useState('Senior Data Analyst')
  const [manager, setManager] = useState('')
  const [jobAd, setJobAd] = useState('')

  async function writeCover() {
    setBusy(true)
    setError('')
    try {
      const result = await api.coverLetter({
        job_title: jobTitle,
        company,
        job_description: jobAd,
        hiring_manager: manager,
        highlights: ['Cut reporting time by 40% by rebuilding the finance dashboard'],
        years_experience: 6,
        seniority: 'senior',
      })
      if (result?.text) setCover(result.text)
      else setError('Could not reach the API. Start the backend and try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {MODES.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setMode(item.id)}
            aria-pressed={mode === item.id}
            className={`inline-flex items-center gap-2 rounded-pill border px-3.5 py-2 text-xs font-semibold transition ${
              mode === item.id
                ? 'border-pop bg-pop/10 text-pop'
                : 'border-line text-dim hover:border-pop/40'
            }`}
          >
            <Icon name={item.icon} className="h-3.5 w-3.5" />
            {item.label}
          </button>
        ))}
      </div>

      {mode === 'cover' ? (
        <div className="mt-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className={label}>
              Company
              <input
                className={`${input} mt-1.5`}
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </label>
            <label className={label}>
              Job title
              <input
                className={`${input} mt-1.5`}
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </label>
            <label className={`${label} sm:col-span-2`}>
              Hiring manager (optional)
              <input
                className={`${input} mt-1.5`}
                value={manager}
                onChange={(e) => setManager(e.target.value)}
                placeholder="Dana Reed"
              />
            </label>
            <label className={`${label} sm:col-span-2`}>
              Paste the advert (optional — we mirror their keywords)
              <textarea
                rows={3}
                className={`${input} mt-1.5 resize-y`}
                value={jobAd}
                onChange={(e) => setJobAd(e.target.value)}
              />
            </label>
          </div>

          <button
            type="button"
            onClick={writeCover}
            disabled={busy}
            className="btn-primary mt-4 inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-bold disabled:opacity-60"
          >
            <Icon name="mail" className="h-4 w-4" />
            {busy ? 'Writing…' : 'Write the cover letter'}
          </button>

          {cover && (
            <pre className="mt-4 max-h-[340px] overflow-auto whitespace-pre-wrap rounded-xl border border-line bg-void/60 p-4 font-sans text-[13px] leading-relaxed text-dim">
              {cover}
            </pre>
          )}
        </div>
      ) : (
        <ResignationForm company={company} setCompany={setCompany} busy={busy} setError={setError} />
      )}

      <div className="mt-7 border-t border-line2 pt-6">
        <CareerTest />
      </div>

      {error && <p className="mt-3 font-mono text-[11px] text-rose">{error}</p>}
    </div>
  )
}
