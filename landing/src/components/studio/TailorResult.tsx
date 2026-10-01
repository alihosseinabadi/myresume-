'use client'

import Icon from '@/components/shared/Icon'
import type { TailorResult as TailorResultType } from '@/lib/api'

/**
 * What the tailor endpoint produced: which job the CV was written for, and the
 * advert keywords still worth adding to it.
 *
 * Deliberately not here:
 *  - a score and a letter grade. Someone opening a shared link read "62 · grade
 *    C" as a verdict on them, not as a hint about wording. The two keyword
 *    lists below say the same useful thing in plain words.
 *  - the summary, bullets and skills. They are already printed on the CV sheet
 *    beside this panel, so repeating them made the screen harder to follow.
 *  - the PDF / DOCX / TXT buttons. They belong to the CV sheet, just above it.
 */
export default function TailorResult({ result }: { result: TailorResultType }) {
  const { resume, job, notes } = result
  const covered = result.matched_keywords.slice(0, 10)
  const missing = result.missing_keywords.slice(0, 10)

  return (
    <div className="mt-6 rounded-2xl border border-line bg-void/50 p-5">
      {!job.ok && job.message && (
        <p className="mb-4 rounded-xl border border-rose/40 bg-rose/10 px-4 py-3 text-[12px] leading-relaxed text-rose">
          {job.message}
        </p>
      )}

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-pop">
            written for
          </p>
          <h4 className="mt-1 text-base font-bold text-text">
            {resume.personal.headline || job.title || 'This role'}
          </h4>
          <p className="mt-0.5 font-mono text-[11px] text-dimmer">
            {[job.company, job.location].filter(Boolean).join('  ·  ')}
          </p>
          {job.engine && (
            <p className="mt-1 font-mono text-[10px] text-dimmer">
              fetched by <span className="text-plum">{job.engine}</span>
              {job.source ? ` · ${job.source}` : ''}
            </p>
          )}
        </div>

        <span className="inline-flex shrink-0 items-center gap-1.5 rounded-pill border border-mint/40 bg-mint/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-mint">
          <Icon name="check" className="h-3 w-3" />
          ready
        </span>
      </div>

      <p className="mt-4 text-[13px] leading-relaxed text-dim">
        Your CV is ready. Save it as PDF, DOCX or TXT with the buttons above your CV.
      </p>

      {(covered.length > 0 || missing.length > 0) && (
        <div className="mt-5 grid gap-4 border-t border-line2 pt-4 sm:grid-cols-2">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-mint">
              in your CV
            </p>
            <p className="mt-1.5 text-[12px] leading-relaxed text-dim">
              {covered.join(', ') || '—'}
            </p>
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
              worth adding, if true
            </p>
            <p className="mt-1.5 text-[12px] leading-relaxed text-dim">
              {missing.join(', ') || '—'}
            </p>
          </div>
        </div>
      )}

      {notes.length > 0 && (
        <ul className="mt-4 space-y-1.5">
          {notes.map((note) => (
            <li key={note} className="font-mono text-[11px] leading-relaxed text-dimmer">
              {note}
            </li>
          ))}
        </ul>
      )}

      <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
        written by {result.provider === 'local' ? 'the offline recruiter engine' : result.provider}
      </p>
    </div>
  )
}
