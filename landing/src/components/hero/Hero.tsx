import Icon from '@/components/shared/Icon'
import PaperCard from '@/components/studio/PaperCard'
import AuditRow from '@/components/sections/AuditRow'
import { FALLBACK_RESUME } from '@/lib/api'

export default function Hero() {
  return (
    <section id="top" className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 left-1/2 h-[560px] w-[900px] -translate-x-1/2 animate-drift rounded-full aurora blur-2xl"
      />

      <div className="shell relative pb-12 pt-12 md:pb-16 md:pt-16">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <span className="eyebrow">No signup · runs instantly</span>

            <h1 className="display mt-5 text-[3rem] text-text sm:text-[3.9rem] lg:text-[4.4rem]">
              A CV that sounds like
              <br />
              your <em className="not-italic text-pop">best day at work</em>.
            </h1>

            <p className="mt-6 max-w-lg text-[15px] leading-relaxed text-dim sm:text-base">
              Type a job title. We write the wording, you restyle it across 11 recruiter-approved
              templates in 24 languages, then check it against the advert before you send it.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a
                href="#studio"
                className="btn-primary inline-flex items-center gap-2 rounded-pill px-6 py-3.5 text-sm font-bold"
              >
                Paste a job link
                <Icon name="arrow" className="h-4 w-4" />
              </a>
              <a
                href="#templates"
                className="inline-flex items-center gap-2 rounded-pill border border-line px-6 py-3.5 text-sm font-semibold text-text transition hover:border-pop/50"
              >
                See the 11 templates
              </a>
            </div>

            <p className="mt-6 font-mono text-[11px] leading-relaxed text-dimmer">
              FastAPI backend · AI provider chain with an offline engine fallback · PDF, DOCX and TXT
              export
            </p>

            <div className="mt-8 border-t border-line2 pt-6">
              <AuditRow />
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-md">
            <div className="absolute -inset-8 -z-10 rounded-[2.5rem] bg-gradient-to-br from-pop/15 via-transparent to-plum/20 blur-3xl" />
            <div className="rotate-[-1.4deg] transition-transform duration-500 hover:rotate-0">
              <PaperCard resume={FALLBACK_RESUME} />
            </div>
            <div className="mt-5 flex flex-wrap items-center justify-center gap-2 font-mono text-[11px]">
              <span className="rounded-lg border border-line bg-panel px-3 py-1.5 text-pop">
                matched to the advert
              </span>
              <span className="rounded-lg border border-line bg-panel px-3 py-1.5 text-dim">
                1 page · ATS-safe
              </span>
              <span className="rounded-lg border border-line bg-panel px-3 py-1.5 text-dim">
                rewritten in 4 min
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
