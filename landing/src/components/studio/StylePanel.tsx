'use client'

import Icon from '@/components/shared/Icon'
import { TEMPLATES } from '@/lib/templates'
import { LOCALES } from '@/lib/seo'

const SHOWN_LOCALES = LOCALES.slice(0, 8)

export default function StylePanel({
  templateId,
  setTemplateId,
  locale,
  setLocale,
  headings,
}: {
  templateId: string
  setTemplateId: (id: string) => void
  locale: string
  setLocale: (code: string) => void
  headings: Record<string, string>
}) {
  return (
    <div>
      <span className="eyebrow">Template</span>
      <p className="mt-2 text-sm text-dim">
        Every template is single-column and machine-readable, so parsers read it cleanly.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {TEMPLATES.map((template) => (
          <button
            key={template.id}
            type="button"
            onClick={() => setTemplateId(template.id)}
            aria-pressed={templateId === template.id}
            className={`inline-flex items-center gap-2 rounded-pill border px-3 py-1.5 text-xs font-semibold transition ${
              templateId === template.id
                ? 'border-pop bg-pop/10 text-pop'
                : 'border-line text-dim hover:border-pop/40'
            }`}
          >
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ background: template.accent }}
              aria-hidden="true"
            />
            {template.name}
          </button>
        ))}
      </div>
      <p className="mt-2.5 font-mono text-[11px] text-dimmer">
        accent {TEMPLATES.find((t) => t.id === templateId)?.accent} ·{' '}
        {TEMPLATES.find((t) => t.id === templateId)?.tagline}
      </p>

      <div className="mt-7 hairline pt-6">
        <span className="eyebrow">Language</span>
        <p className="mt-2 text-sm text-dim">
          Headings are translated while the layout stays exactly the same.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {SHOWN_LOCALES.map((item) => (
            <button
              key={item.code}
              type="button"
              onClick={() => setLocale(item.code)}
              aria-pressed={locale === item.code}
              className={`rounded-lg border px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider transition ${
                locale === item.code
                  ? 'border-pop bg-pop text-void'
                  : 'border-line text-dim hover:border-pop/40'
              }`}
            >
              {item.code}
            </button>
          ))}
          <span className="inline-flex items-center rounded-lg border border-line2 px-3 py-1.5 font-mono text-[11px] text-dimmer">
            +16 more
          </span>
        </div>

        <div className="mt-4 rounded-xl border border-line bg-void/60 p-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
            live heading translation
          </p>
          <ul className="mt-3 space-y-1.5 font-mono text-[12px] text-dim">
            {Object.keys(headings).length > 0 ? (
              Object.entries(headings).map(([from, to]) => (
                <li key={from} className="flex items-center gap-2">
                  <span className="text-dimmer">{from}</span>
                  <Icon name="arrow" className="h-3 w-3 text-pop" />
                  <span className="text-pop">{to}</span>
                </li>
              ))
            ) : (
              <li className="text-dimmer">
                Pick a language above — English is the source, so nothing changes.
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}
