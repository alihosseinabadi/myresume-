import Logo from '@/components/shared/Logo'
import { TOOL_TARGETS, TOOLS } from '@/lib/content'

/** Only links that go somewhere; everything else is plain text. */
const MORE_LINKS: { label: string; href: string }[] = [{ label: 'Pricing', href: '#pricing' }]

export default function SiteFooter() {
  return (
    <footer className="border-t border-line bg-ink">
      <div className="shell py-14">
        <div className="grid gap-10 md:grid-cols-[1.3fr_1fr_1fr]">
          <div>
            <Logo />
            <p className="mt-5 max-w-sm text-sm leading-relaxed text-dim">
              One panel that writes with you, restyles your CV across 11 recruiter-approved
              templates, checks it against the words the job ad uses and exports it ATS-safe.
            </p>
            <p className="mt-5 font-mono text-[11px] leading-relaxed text-dimmer">
              FastAPI + Next.js. The AI chain falls back to a deterministic offline engine, so
              drafting never fails.
            </p>
          </div>

          <nav aria-label="Tools">
            <h2 className="font-mono text-[11px] uppercase tracking-[0.2em] text-dimmer">Tools</h2>
            <ul className="mt-4 space-y-2.5">
              {TOOLS.map((tool) => {
                const target = TOOL_TARGETS[tool.id]
                return (
                  <li key={tool.id}>
                    {target ? (
                      <a href={target} className="text-sm text-dim transition hover:text-pop">
                        {tool.name}
                      </a>
                    ) : (
                      <span className="text-sm text-dimmer">{tool.name}</span>
                    )}
                  </li>
                )
              })}
            </ul>
          </nav>

          <nav aria-label="More">
            <h2 className="font-mono text-[11px] uppercase tracking-[0.2em] text-dimmer">More</h2>
            <ul className="mt-4 space-y-2.5">
              {MORE_LINKS.map((item) => (
                <li key={item.href}>
                  <a href={item.href} className="text-sm text-dim transition hover:text-pop">
                    {item.label}
                  </a>
                </li>
              ))}
              <li className="pt-2 font-mono text-[11px] leading-relaxed text-dimmer">
                About, legal pages and an account area are not built yet — we would rather say so
                than link to nothing.
              </li>
            </ul>
          </nav>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-line2 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-mono text-[11px] text-dimmer">
            © {new Date().getFullYear()} MyResume Studio — all rights reserved
          </p>
          <p className="max-w-xl font-mono text-[11px] leading-relaxed text-dimmer">
            9 tools · 11 templates · 24 locales · company names are trademarks of their owners
          </p>
        </div>
      </div>
    </footer>
  )
}
