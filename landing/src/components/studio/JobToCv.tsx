'use client'

import { useEffect, useRef, useState } from 'react'
import Icon from '@/components/shared/Icon'
import TailorResult from '@/components/studio/TailorResult'
import ShareLink from '@/components/share/ShareLink'
import { api, type Resume } from '@/lib/api'
import { briefToInput, firstName, type ShareBrief } from '@/lib/share'

const SAMPLE_ADVERT =
  'Senior Data Analyst wanted. You will own experimentation and reporting using SQL, Python, dbt and Airflow. Partner with product on A/B testing, build Tableau dashboards for finance, and do causal inference. Stakeholder management and forecasting experience required. Mentor two analysts.'

const CHIPS = [
  { label: 'Sample advert', value: SAMPLE_ADVERT },
  { label: 'Data Analyst', value: 'Data Analyst' },
  { label: 'Product Manager', value: 'Product Manager' },
  { label: 'Registered Nurse', value: 'Registered Nurse' },
]

const isUrl = (value: string) => /^https?:\/\/\S+$/i.test(value.trim())

/** The advert fields we hand to the API. */
type JobInput = { url: string; job_description: string; job_title: string }

/**
 * Turn the input box into an API payload.
 *
 * A shared brief already knows the URL, the advert text and the title, so it
 * sends all three at once (the backend prefers the URL) and only treats the box
 * as an override once the visitor has actually edited it.
 */
function resolveJobInput(text: string, brief?: ShareBrief): JobInput {
  if (brief) {
    const edited = text.trim() !== briefToInput(brief).trim()
    return {
      url: brief.url ?? '',
      job_description: edited ? text : brief.text ?? '',
      job_title: brief.role ?? '',
    }
  }
  return isUrl(text)
    ? { url: text, job_description: '', job_title: '' }
    : text.length > 90
      ? { url: '', job_description: text, job_title: '' }
      : { url: '', job_description: '', job_title: text }
}

/**
 * The headline flow: give us a job link (or paste the advert, or just name the
 * role) and the API returns a CV written for that job, plus what that advert
 * still wants from it.
 *
 * With a shared `brief` the box arrives pre-filled, the recipient's own name goes
 * on the CV, and it is built once on arrival so the page is never empty.
 */
export default function JobToCv({
  brief,
  onResume,
  template,
  locale,
}: {
  brief?: ShareBrief
  onResume: (resume: Resume) => void
  template: string
  locale: string
}) {
  const [value, setValue] = useState(() => briefToInput(brief))
  const [candidateName, setCandidateName] = useState(() => brief?.to ?? '')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<Awaited<ReturnType<typeof api.tailor>>>(null)
  const [error, setError] = useState('')
  const arrived = useRef(false)

  const sender = brief ? firstName(brief.from) : ''
  const hasBriefedJob = Boolean(brief?.url || brief?.text || brief?.role)
  // The role, without the generated "Role | skill, skill" headline tail — sending
  // the whole headline on would make the next engine append its own skills again.
  const shareRole = result
    ? (result.job.title || result.resume.personal.headline).split('|')[0].trim()
    : ''

  async function build() {
    const text = value.trim()
    if (!text && !hasBriefedJob) {
      setError('Paste a job link, the advert text, or a job title first.')
      return
    }
    setBusy(true)
    setError('')
    try {
      const tailored = await api.tailor({
        ...resolveJobInput(text, brief),
        template,
        locale,
        full_name: candidateName.trim(),
      })
      if (tailored) {
        setResult(tailored)
        onResume(tailored.resume)
      } else {
        setError(
          brief
            ? 'The engine is not answering, so the CV could not be built yet. Press build to try again.'
            : 'Could not reach the API. Start the backend and try again.',
        )
      }
    } finally {
      setBusy(false)
    }
  }

  // A link that already carries a job builds itself once, so the recipient lands
  // on a finished CV instead of an empty box.
  useEffect(() => {
    if (arrived.current || !hasBriefedJob) return
    arrived.current = true
    void build()
    // Runs on arrival only: later edits are the visitor's own.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div>
      <span className="eyebrow">
        {brief ? `Briefed by ${sender || 'a friend'}` : 'From a job link'}
      </span>
      <h3 className="display mt-3 text-3xl text-text sm:text-4xl">
        {brief ? 'Your CV, already briefed.' : 'Paste the advert. Get the CV.'}
      </h3>
      <p className="mt-3 max-w-lg text-sm leading-relaxed text-dim">
        {brief
          ? 'The advert came with the link. Put your name on it, press build, and download the PDF.'
          : 'We read the posting, then write your summary, bullets and skills around its own keywords.'}
      </p>

      {brief && (
        <label className="mt-5 block">
          <span className="flex flex-wrap items-baseline gap-2">
            <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
              Your name on the CV
            </span>
            <span className="font-mono text-[10px] text-dimmer/70">
              edit it, then build again
            </span>
          </span>
          <input
            value={candidateName}
            onChange={(event) => setCandidateName(event.target.value)}
            placeholder="Your full name"
            aria-label="Your name on the CV"
            className="mt-1.5 w-full rounded-xl border border-line bg-void/60 px-4 py-3 text-sm text-text outline-none transition placeholder:text-dimmer focus:border-pop"
          />
        </label>
      )}

      <div className="mt-5 flex flex-col gap-2 sm:flex-row">
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') build()
          }}
          placeholder="https://jobs.acme.com/data-analyst   —   or paste the ad   —   or type a title"
          aria-label="Job link, advert text or job title"
          className="w-full rounded-xl border border-line bg-void/60 px-4 py-3.5 text-sm text-text outline-none transition placeholder:text-dimmer focus:border-pop"
        />
        <button
          type="button"
          onClick={build}
          disabled={busy}
          className="btn-primary inline-flex shrink-0 items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-sm font-bold disabled:opacity-60"
        >
          <Icon name="sparkle" className="h-4 w-4" />
          {busy ? 'Building…' : 'Build my CV'}
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {CHIPS.map((chip) => (
          <button
            key={chip.label}
            type="button"
            onClick={() => setValue(chip.value)}
            className="rounded-pill border border-line px-3 py-1.5 font-mono text-[11px] text-dimmer transition hover:border-pop/50 hover:text-dim"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {error && (
        <p className="mt-3 font-mono text-[11px] text-rose">{error}</p>
      )}

      {result && (
        <>
          <TailorResult result={result} />
          <ShareLink
            seed={{
              // Whoever built it last becomes the sender of the next link.
              from: candidateName.trim(),
              role: shareRole,
              jobUrl: result.job.url,
              advertText: result.job.description,
              template,
              locale,
            }}
          />
        </>
      )}
    </div>
  )
}
