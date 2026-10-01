import { HIRED_BY } from '@/lib/marketing'

/** One thin proof line. No logo grid, no disclaimers — the footer covers that. */
export default function Marquee() {
  const words = [...HIRED_BY, ...HIRED_BY]

  return (
    <section className="overflow-hidden border-y border-line2 py-5">
      <div className="flex items-center gap-6">
        <span className="hidden shrink-0 pl-6 font-mono text-[10px] uppercase tracking-[0.2em] text-dimmer md:block">
          users hired at
        </span>
        <div className="relative flex-1 overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_10%,#000_90%,transparent)]">
          <ul className="flex w-max animate-marquee items-center gap-10" aria-hidden="true">
            {words.map((company, index) => (
              <li
                key={`${company}-${index}`}
                className="shrink-0 font-mono text-sm uppercase tracking-[0.12em] text-dimmer"
              >
                {company}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
