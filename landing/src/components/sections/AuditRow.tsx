import { STATS } from '@/lib/content'

/** Compact proof row under the hero — four numbers, no card grid. */
export default function AuditRow() {
  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
      {STATS.map((stat) => (
        <div key={stat.label}>
          <dt className="display text-3xl text-pop">{stat.value}</dt>
          <dd className="mt-1 font-mono text-[10px] uppercase leading-relaxed tracking-[0.14em] text-dimmer">
            {stat.label}
          </dd>
        </div>
      ))}
    </dl>
  )
}
