import { FAQS } from '@/lib/marketing'

const SHORT = FAQS.slice(0, 5)

/** Five questions, native <details> — works without JavaScript. */
export default function FaqShort() {
  return (
    <section id="faq" className="scroll-mt-20 border-t border-line2 py-16 md:py-20">
      <div className="shell grid gap-10 lg:grid-cols-[0.75fr_1.25fr]">
        <div>
          <span className="eyebrow">FAQ</span>
          <h2 className="display mt-3 text-4xl text-text sm:text-5xl">Before you ask</h2>
          <p className="mt-4 text-sm leading-relaxed text-dim">
            Everything you need to know about building, scoring and exporting your CV.
          </p>
          <a
            href="#studio"
            className="btn-primary mt-6 inline-flex items-center gap-2 rounded-pill px-5 py-3 text-sm font-bold"
          >
            Try it now
          </a>
        </div>

        <div className="divide-y divide-line2 border-y border-line2">
          {SHORT.map((faq, index) => (
            <details key={faq.q} className="group" open={index === 0}>
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-left text-[15px] font-semibold text-text marker:hidden">
                {faq.q}
                <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-line font-mono text-dim transition group-open:rotate-45 group-open:border-pop group-open:text-pop">
                  +
                </span>
              </summary>
              <p className="pb-5 pr-10 text-sm leading-relaxed text-dim">{faq.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  )
}
