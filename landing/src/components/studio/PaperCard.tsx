import type { Resume } from '@/lib/api'

/**
 * The CV itself, rendered as a white sheet against the dark canvas.
 * Takes a real `Resume` (from the API or the local fallback) and honours its
 * accent colour, so template switching is visible here.
 */
export default function PaperCard({
  resume,
  compact = false,
}: {
  resume: Resume
  compact?: boolean
}) {
  const accent = resume.accent_color || '#0F766E'

  return (
    <article
      className={`w-full rounded-2xl bg-white text-void shadow-[0_40px_90px_-45px_rgba(0,0,0,0.95)] ${
        compact ? 'p-3 text-[6px] leading-[1.5]' : 'p-6 text-[11px] leading-relaxed sm:p-7'
      }`}
    >
      <header className={compact ? 'mb-2' : 'mb-4'}>
        <h3
          className={`font-bold tracking-tight ${compact ? 'text-[9px]' : 'text-lg sm:text-xl'}`}
          style={{ color: accent }}
        >
          {resume.personal.full_name || 'Your name'}
        </h3>
        {resume.personal.headline && (
          <p className={compact ? 'text-[6px] text-slate-600' : 'text-[12px] text-slate-600'}>
            {resume.personal.headline}
          </p>
        )}
        {!compact && (
          <p className="mt-1 text-[10px] text-slate-500">
            {[resume.personal.email, resume.personal.phone, resume.personal.location]
              .filter(Boolean)
              .join('  ·  ')}
          </p>
        )}
        <span className="mt-2.5 block h-[2px] w-full rounded" style={{ background: accent }} />
      </header>

      {resume.summary && (
        <Block label="Summary" accent={accent} compact={compact}>
          <p>{resume.summary}</p>
        </Block>
      )}

      {resume.experience.map((item) => (
        <Block key={item.id} label={item.role} accent={accent} compact={compact}>
          {!compact && (
            <p className="text-[10px] text-slate-500">
              {[item.company, item.location, [item.start_date, item.current ? 'Present' : item.end_date].filter(Boolean).join(' – ')]
                .filter(Boolean)
                .join('  ·  ')}
            </p>
          )}
          <ul className={`space-y-1 ${compact ? 'text-[6px]' : 'text-[11px]'}`}>
            {item.bullets.slice(0, compact ? 2 : 3).map((bullet) => (
              <li key={bullet} className="flex gap-1.5">
                <span aria-hidden="true" style={{ color: accent }}>
                  •
                </span>
                <span>{bullet}</span>
              </li>
            ))}
          </ul>
        </Block>
      ))}

      {resume.education.length > 0 && (
        <Block label="Education" accent={accent} compact={compact}>
          {resume.education.map((item) => (
            <p key={item.id}>
              <span className="font-semibold">{item.degree}</span>
              {item.school ? ` — ${item.school}` : ''}
            </p>
          ))}
        </Block>
      )}

      {resume.skills.map((group) => (
        <Block key={group.id} label={group.name} accent={accent} compact={compact}>
          <p>{group.skills.join(' · ')}</p>
        </Block>
      ))}
    </article>
  )
}

function Block({
  label,
  accent,
  compact,
  children,
}: {
  label: string
  accent: string
  compact: boolean
  children: React.ReactNode
}) {
  return (
    <section className={compact ? 'mb-1.5' : 'mb-3'}>
      <h4
        className={`font-bold uppercase tracking-[0.12em] ${
          compact ? 'mb-0.5 text-[6px]' : 'mb-1 text-[9px]'
        }`}
        style={{ color: accent }}
      >
        {label}
      </h4>
      <div className={compact ? 'space-y-0.5' : 'space-y-1'}>{children}</div>
    </section>
  )
}
