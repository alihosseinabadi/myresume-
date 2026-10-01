import Icon from '@/components/shared/Icon'
import { LOCALES } from '@/lib/seo'
import { TEMPLATES } from '@/lib/templates'
import { firstName, hostOf, type ShareBrief } from '@/lib/share'

/**
 * The recipient's greeting: who sent the link, what role it is written for and
 * which template/language they chose. Rendered on the server, so it is in the
 * HTML a crawler or a no-JS visitor receives.
 */
export default function GiftHero({ brief }: { brief: ShareBrief }) {
  const sender = firstName(brief.from)
  const recipient = firstName(brief.to)
  const role = brief.role
  const host = hostOf(brief.url)
  const template = TEMPLATES.find((item) => item.id === brief.template)
  const language = LOCALES.find((item) => item.code === brief.locale)

  const title = recipient
    ? `Hi ${recipient} — ${sender || 'a friend'} sent you a head start.`
    : `${sender || 'Someone'} sent you a head start.`

  const body = role
    ? `The CV below is already written around ${recipient ? 'your' : 'the'} target: ${role}. ` +
      'Add your name, press build, and the summary, bullets and skills come out matching that advert — then take the PDF.'
    : 'The job advert travels inside this link. Add your name, press build, and the CV comes out written for that job — then take the PDF.'

  const chips = [
    sender ? { label: 'from', value: sender } : null,
    role ? { label: 'written for', value: role } : null,
    host ? { label: 'advert', value: host } : null,
    !host && brief.text ? { label: 'advert', value: 'pasted by the sender' } : null,
    template ? { label: 'template', value: template.name } : null,
    language ? { label: 'language', value: language.label } : null,
  ].filter(Boolean) as { label: string; value: string }[]

  return (
    <section className="relative overflow-hidden pt-10">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-36 left-1/2 h-[380px] w-[780px] -translate-x-1/2 animate-drift rounded-full aurora blur-2xl"
      />

      <div className="shell relative">
        <div className="panel p-6 sm:p-8">
          <div className="flex flex-wrap items-start gap-5">
            <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-pop text-void">
              <Icon name="gift" className="h-6 w-6" />
            </span>

            <div className="min-w-0 flex-1">
              <span className="eyebrow">A CV brief, sent to you</span>
              <h1 className="display mt-3 text-[2.1rem] text-text sm:text-[2.7rem]">{title}</h1>
              <p className="mt-3 max-w-2xl text-[15px] leading-relaxed text-dim">{body}</p>

              {brief.note && (
                <blockquote className="mt-4 border-l-2 border-pop pl-4 text-[14px] italic leading-relaxed text-text">
                  “{brief.note}”
                  {sender && (
                    <span className="not-italic text-dimmer"> — {sender}</span>
                  )}
                </blockquote>
              )}

              <div className="mt-5 flex flex-wrap items-center gap-2">
                {chips.map((chip) => (
                  <span
                    key={chip.label}
                    className="rounded-lg border border-line bg-panel/70 px-2.5 py-1 text-[11px] text-dim"
                  >
                    <span className="font-mono text-[10px] uppercase tracking-wider text-dimmer">
                      {chip.label}
                    </span>{' '}
                    {chip.value}
                  </span>
                ))}
                <a
                  href="/"
                  className="inline-flex items-center gap-1 font-mono text-[11px] text-pop transition hover:text-text"
                >
                  start from scratch instead
                  <Icon name="arrow" className="h-3 w-3" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
