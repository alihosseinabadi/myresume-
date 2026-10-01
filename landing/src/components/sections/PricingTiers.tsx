import Icon from '@/components/shared/Icon'
import { PRICING } from '@/lib/marketing'

/** Three tiers, minimal chrome — one highlighted. */
export default function PricingTiers() {
  return (
    <section id="pricing" className="scroll-mt-20 py-16 md:py-20">
      <div className="shell">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <span className="eyebrow">Pricing</span>
            <h2 className="display mt-3 text-4xl text-text sm:text-5xl">
              One subscription, every tool
            </h2>
          </div>
          <p className="max-w-sm text-sm leading-relaxed text-dim">
            CV builder, cover letters, the ATS checker, resignation letters and priority support.
            Cancel whenever.
          </p>
        </div>

        <ul className="mt-10 grid gap-5 lg:grid-cols-3">
          {PRICING.map((plan) => (
            <li
              key={plan.id}
              className={`relative flex flex-col rounded-card border p-6 ${
                plan.highlight
                  ? 'border-pop bg-gradient-to-b from-pop/10 to-transparent'
                  : 'border-line bg-panel/40'
              }`}
            >
              {plan.badge && (
                <span
                  className={`absolute -top-2.5 left-6 rounded-pill px-3 py-1 font-mono text-[9px] uppercase tracking-[0.14em] ${
                    plan.highlight ? 'bg-pop text-void' : 'bg-panel2 text-dim'
                  }`}
                >
                  {plan.badge}
                </span>
              )}

              <h3 className="font-mono text-[11px] uppercase tracking-[0.16em] text-dim">
                {plan.name}
              </h3>
              <p className="mt-3 flex items-baseline gap-2">
                <span className="display text-5xl text-text">{plan.price}</span>
                <span className="font-mono text-[11px] text-dimmer">{plan.period}</span>
              </p>

              <ul className="mt-5 flex-1 space-y-2.5">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex gap-2.5 text-[13px] text-dim">
                    <Icon name="check" className="mt-0.5 h-3.5 w-3.5 shrink-0 text-pop" />
                    {feature}
                  </li>
                ))}
              </ul>

              <a
                href="#studio"
                className={`mt-6 inline-flex items-center justify-center gap-2 rounded-pill px-5 py-3 text-sm font-bold transition ${
                  plan.highlight ? 'btn-primary' : 'border border-line text-text hover:border-pop/60'
                }`}
              >
                {plan.cta}
              </a>
              <span className="mt-3 font-mono text-[10px] leading-relaxed text-dimmer">
                {plan.note}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
