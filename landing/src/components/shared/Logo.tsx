/** Wordmark, lime on dark. */
export default function Logo() {
  return (
    <span className="flex items-center gap-2.5">
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-pop text-void shadow-[0_10px_24px_-12px_rgba(198,242,78,0.9)]">
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M14 3v5h5" />
          <path d="M15 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
          <path d="m9 14 2 2 4-4" />
        </svg>
      </span>
      <span className="text-lg font-bold tracking-tight text-text">
        My<span className="text-pop">Resume</span>
        <span className="ml-2 hidden font-mono text-[10px] font-semibold uppercase tracking-[0.2em] text-dimmer sm:inline">
          studio
        </span>
      </span>
    </span>
  )
}
