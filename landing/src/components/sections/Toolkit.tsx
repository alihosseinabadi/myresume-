'use client'

import { useState } from 'react'
import Icon from '@/components/shared/Icon'
import { PLANNED_NOTE, TOOL_TARGETS, TOOLS } from '@/lib/content'

/**
 * Every chip either opens the studio at the right tool (`#tool=…`) or, for the
 * tools we have not built, says so plainly — there are no dead links.
 */
export default function Toolkit() {
  const [note, setNote] = useState('')

  return (
    <section id="toolkit" className="scroll-mt-20 py-16 md:py-20">
      <div className="shell">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <span className="eyebrow">Everything in the box</span>
            <h2 className="display mt-3 text-4xl text-text sm:text-5xl">Nine tools, one panel</h2>
          </div>
          <p className="max-w-sm text-sm leading-relaxed text-dim">
            Start with the CV. The cover letter, resignation letter, ATS report and career test are
            one click away — no switching tabs, no second account.
          </p>
        </div>

        <ul className="mt-9 flex flex-wrap gap-2.5">
          {TOOLS.map((tool) => {
            const target = TOOL_TARGETS[tool.id]
            const inner = (
              <>
                <Icon name={tool.icon} className="h-4 w-4 text-pop" />
                <span className="text-sm font-medium text-text">{tool.name}</span>
                {tool.badge && (
                  <span className="rounded-pill bg-pop/15 px-2 py-0.5 font-mono text-[9px] uppercase tracking-wider text-pop">
                    {tool.badge}
                  </span>
                )}
                {!target && (
                  <span className="rounded-pill border border-line px-2 py-0.5 font-mono text-[9px] uppercase tracking-wider text-dimmer">
                    planned
                  </span>
                )}
              </>
            )

            return (
              <li key={tool.id}>
                {target ? (
                  <a
                    href={target}
                    className="flex items-center gap-2.5 rounded-pill border border-line bg-panel/60 px-4 py-2.5 transition hover:border-pop/60"
                  >
                    {inner}
                  </a>
                ) : (
                  <button
                    type="button"
                    onClick={() => setNote(tool.id)}
                    aria-describedby="toolkit-note"
                    className="flex items-center gap-2.5 rounded-pill border border-dashed border-line bg-panel/30 px-4 py-2.5 opacity-80 transition hover:border-plum/60 hover:opacity-100"
                  >
                    {inner}
                  </button>
                )}
              </li>
            )
          })}
        </ul>

        <p id="toolkit-note" aria-live="polite" className="mt-5 min-h-4 font-mono text-[11px] text-plum">
          {note ? PLANNED_NOTE : ''}
        </p>
      </div>
    </section>
  )
}
