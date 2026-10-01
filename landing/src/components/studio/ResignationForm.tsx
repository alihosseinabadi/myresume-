'use client'

import { useState } from 'react'
import Icon from '@/components/shared/Icon'
import { api, type Resignation } from '@/lib/api'

const input =
  'w-full rounded-xl border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text outline-none transition placeholder:text-dimmer focus:border-pop'
const label = 'block text-xs font-semibold uppercase tracking-wider text-dimmer'

/** Short, professional resignation letters — from the API, never invented facts. */
export default function ResignationForm({
  company,
  setCompany,
  busy,
  setError,
}: {
  company: string
  setCompany: (value: string) => void
  busy: boolean
  setError: (value: string) => void
}) {
  const [name, setName] = useState('')
  const [role, setRole] = useState('')
  const [lastDay, setLastDay] = useState('')
  const [reason, setReason] = useState('')
  const [highlight, setHighlight] = useState('')
  const [result, setResult] = useState<Resignation | null>(null)
  const [saving, setSaving] = useState(false)

  async function write() {
    setSaving(true)
    setError('')
    try {
      const response = await api.resignation({
        full_name: name,
        job_title: role,
        company,
        last_working_day: lastDay,
        reason,
        highlight,
      })
      if (response?.letter) setResult(response)
      else setError('Could not reach the API. Start the backend and try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mt-5">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className={label}>
          Your name
          <input
            className={`${input} mt-1.5`}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Alex Morgan"
          />
        </label>
        <label className={label}>
          Your role
          <input
            className={`${input} mt-1.5`}
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="Data Analyst"
          />
        </label>
        <label className={label}>
          Company
          <input className={`${input} mt-1.5`} value={company} onChange={(e) => setCompany(e.target.value)} />
        </label>
        <label className={label}>
          Last working day
          <input
            className={`${input} mt-1.5`}
            value={lastDay}
            onChange={(e) => setLastDay(e.target.value)}
            placeholder="28 February 2026"
          />
        </label>
        <label className={`${label} sm:col-span-2`}>
          Reason (optional — we never invent one)
          <input
            className={`${input} mt-1.5`}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="relocating to Lisbon"
          />
        </label>
        <label className={`${label} sm:col-span-2`}>
          What should be remembered
          <input
            className={`${input} mt-1.5`}
            value={highlight}
            onChange={(e) => setHighlight(e.target.value)}
            placeholder="building the self-serve reporting layer"
          />
        </label>
      </div>

      <button
        type="button"
        onClick={write}
        disabled={saving}
        className="btn-primary mt-4 inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-bold disabled:opacity-60"
      >
        <Icon name="pen" className="h-4 w-4" />
        {saving ? 'Writing…' : 'Write the resignation letter'}
      </button>

      {result && (
        <div className="mt-4">
          <pre className="max-h-[300px] overflow-auto whitespace-pre-wrap rounded-xl border border-line bg-void/60 p-4 font-sans text-[13px] leading-relaxed text-dim">
            {result.letter}
          </pre>
          {result.checklist.length > 0 && (
            <ul className="mt-3 space-y-1.5">
              {result.checklist.map((item) => (
                <li key={item} className="flex gap-2 text-[12px] text-dimmer">
                  <Icon name="check" className="mt-0.5 h-3.5 w-3.5 shrink-0 text-mint" />
                  {item}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
