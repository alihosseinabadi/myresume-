import Icon from '@/components/shared/Icon'
import { TEMPLATES } from '@/lib/templates'

/** One-page mock drawn from CSS blocks, tinted with the template accent. */
function MiniPaper({ accent }: { accent: string }) {
  return (
    <div className="aspect-[3/4] w-full overflow-hidden rounded-lg bg-white p-3" aria-hidden="true">
      <div className="h-1.5 w-2/3 rounded-full" style={{ background: accent }} />
      <div className="mt-1.5 h-1 w-1/3 rounded-full bg-slate-200" />
      <div className="mt-3 space-y-1.5">
        <div className="h-1.5 w-1/2 rounded-full" style={{ background: accent, opacity: 0.55 }} />
        <div className="h-1 w-full rounded-full bg-slate-200" />
        <div className="h-1 w-full rounded-full bg-slate-200" />
        <div className="h-1 w-10/12 rounded-full bg-slate-200" />
        <div className="mt-2 h-1.5 w-1/3 rounded-full" style={{ background: accent, opacity: 0.55 }} />
        <div className="h-1 w-11/12 rounded-full bg-slate-200" />
        <div className="h-1 w-full rounded-full bg-slate-200" />
        <div className="h-1 w-8/12 rounded-full bg-slate-200" />
        <div className="mt-2 h-1.5 w-1/4 rounded-full" style={{ background: accent, opacity: 0.55 }} />
        <div className="h-1 w-full rounded-full bg-slate-200" />
        <div className="h-1 w-9/12 rounded-full bg-slate-200" />
      </div>
    </div>
  )
}

/** All 11 templates on one horizontal rail — scroll, don't scroll the page. */
export default function TemplateRail() {
  return (
    <section id="templates" className="scroll-mt-20 border-y border-line2 py-16 md:py-20">
      <div className="shell">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <span className="eyebrow">Templates</span>
            <h2 className="display mt-3 text-4xl text-text sm:text-5xl">Pick a look, keep the words</h2>
          </div>
          <p className="max-w-sm text-sm leading-relaxed text-dim">
            Switch template at any time — your content is untouched. Drag the rail to see all eleven.
          </p>
        </div>
      </div>

      <div className="rail mt-9 px-5 md:px-8">
        {TEMPLATES.map((template) => (
            <a
              key={template.id}
              href="#tool=style"
              className="group w-[186px] rounded-card border border-line bg-panel/50 p-3 transition hover:border-pop/50"
            >
            <MiniPaper accent={template.accent} />
            <div className="mt-3 flex items-center justify-between gap-2">
              <span className="text-sm font-semibold text-text">{template.name}</span>
              <span className="font-mono text-[9px] uppercase tracking-wider text-pop">ATS</span>
            </div>
            <span className="mt-1 block font-mono text-[10px] leading-relaxed text-dimmer">
              {template.tagline}
            </span>
            <span className="mt-2.5 inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-wider text-dim transition group-hover:text-pop">
              use in studio <Icon name="arrow" className="h-3 w-3" />
            </span>
          </a>
        ))}
      </div>
    </section>
  )
}
