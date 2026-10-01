'use client'

import { useState } from 'react'
import Icon from '@/components/shared/Icon'
import { api, type CareerMatch } from '@/lib/api'

const input =
  'w-full rounded-xl border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text outline-none transition placeholder:text-dimmer focus:border-pop'
const label = 'block text-xs font-semibold uppercase tracking-wider text-dimmer'

/** Career test — instant, ontology-driven, no LLM. */
export default function CareerTest() {
  const [strength, setStrength] = useState<'ideas' | 'data' | 'people' | 'operations'>('data')
  const [interests, setInterests] = useState('')
  const [years, setYears] = useState(4)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CareerMatch | null>(null)
  const [error, setError] = useState('')

  async function run() {
    setBusy(true)
    setError('')
    try {
      const response = await api.careerMatch({
        strength,
        interests,
        years_experience: years,
        seniority: years >= 8 ? 'senior' : years <= 1 ? 'junior' : 'mid',
      })
      if (response) setResult(response)
      else setError('Could not reach the API. Start the backend and try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <span className="eyebrow">Career test</span>
      <p className="mt-2 text-sm text-dim">Two questions, instant answer — no LLM needed.</p>

      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        <label className={label}>
          Strongest at
          <select
            className={`${input} mt-1.5`}
            value={strength}
            onChange={(e) => setStrength(e.target.value as typeof strength)}
          >
            <option value="ideas">Ideas</option>
            <option value="data">Data</option>
            <option value="people">People</option>
            <option value="operations">Operations</option>
          </select>
        </label>
        <label className={label}>
          Interested in
          <input
            className={`${input} mt-1.5`}
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            placeholder="SQL, dashboards"
          />
        </label>
        <label className={label}>
          Years of experience
          <input
            type="number"
            min={0}
            max={40}
            className={`${input} mt-1.5`}
            value={years}
            onChange={(e) => setYears(Number(e.target.value))}
          />
        </label>
      </div>

      <button
        type="button"
        onClick={run}
        disabled={busy}
        className="mt-3 inline-flex items-center gap-2 rounded-xl border border-line px-4 py-2.5 text-sm font-semibold text-text transition hover:border-pop/50 disabled:opacity-60"
      >
        <Icon name="compass" className="h-4 w-4 text-pop" />
        {busy ? 'Thinking…' : 'Find my roles'}
      </button>

      {result && (
        <div className="mt-4 rounded-xl border border-line bg-void/60 p-4">
          <p className="text-[13px] leading-relaxed text-dim">{result.note}</p>
          <ul className="mt-3 space-y-2">
            {result.roles.map((item) => (
              <li key={`${item.family}-${item.title}`} className="flex gap-2 text-[13px] text-dim">
                <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-mint" aria-hidden="true" />
                <span>
                  <strong className="text-text">{item.title}</strong>
                  <span className="text-dimmer"> — {item.why}</span>
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
            skills worth listing
          </p>
          <p className="mt-1.5 text-[12px] text-dim">{result.skills.join(' · ')}</p>
        </div>
      )}

      {error && <p className="mt-3 font-mono text-[11px] text-rose">{error}</p>}
    </div>
  )
}
