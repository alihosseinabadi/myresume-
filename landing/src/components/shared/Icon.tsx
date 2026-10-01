/** Inline SVG icon set — stroke-based, no icon dependency. */

const PATHS: Record<string, string[]> = {
  file: ['M14 3v5h5', 'M15 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'],
  mail: ['M3 6h18v12H3z', 'm3 7 9 6 9-6'],
  scan: ['M4 7V4h3M20 7V4h-3M4 17v3h3M20 17v3h-3M4 12h16'],
  pen: ['M12 20h9', 'M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z'],
  camera: ['M4 8h3l1.5-2h7L17 8h3v11H4z', 'M12 16.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z'],
  compass: ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z', 'M15 9l-2 6-4 1 2-6z'],
  search: ['M11 17a6 6 0 1 0 0-12 6 6 0 0 0 0 12z', 'm20 20-4.5-4.5'],
  kanban: ['M5 4h4v16H5z', 'M15 4h4v10h-4z'],
  globe: ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z', 'M3 12h18', 'M12 3c3 3.5 3 14.5 0 18-3-3.5-3-14.5 0-18'],
  sparkle: ['M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'],
  library: ['M4 5h4v14H4z', 'M10 5h4v14h-4z', 'M17 6l3 13'],
  wand: ['M4 20 15 9', 'M14 4l1 2 2 1-2 1-1 2-1-2-2-1 2-1z'],
  shield: ['M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z'],
  check: ['m4 12 5 5L20 6'],
  star: ['M12 3.5l2.7 5.9 6.3.7-4.7 4.3 1.3 6.1L12 17.3l-5.6 3.2 1.3-6.1L3 10.1l6.3-.7z'],
  arrow: ['M5 12h13', 'M13 6l6 6-6 6'],
  menu: ['M4 7h16M4 12h16M4 17h16'],
  close: ['M6 6l12 12M18 6 6 18'],
  download: ['M12 4v11m0 0 4-4m-4 4-4-4', 'M5 20h14'],
  translate: ['M4 6h9', 'M8 6c0 4-2 8-4 10', 'M7 12c1.5 3 4 4.5 6 5', 'm13 20 4-10 4 10', 'M15 16h4'],
  users: ['M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z', 'M2 20c0-3 2.7-5 6-5s6 2 6 5', 'M17 11a3 3 0 1 0 0-6', 'M16 20c0-2 .5-3.5 2-4.5'],
  plus: ['M12 5v14M5 12h14'],
  link: ['M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1', 'M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1'],
  share: ['M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7', 'M12 15V3', 'M8 7l4-4 4 4'],
  copy: ['M9 9h11v11H9z', 'M15 5H5v10'],
  gift: ['M4 11h16v9H4z', 'M2 7h20v4H2z', 'M12 7v13', 'M12 7S11 3.4 8.6 3.4a2.3 2.3 0 0 0 0 3.6z', 'M12 7s1-3.6 3.4-3.6a2.3 2.3 0 0 1 0 3.6z'],
}

export type IconName = keyof typeof PATHS

export default function Icon({
  name,
  className = 'h-5 w-5',
  filled = false,
}: {
  name: string
  className?: string
  filled?: boolean
}) {
  const paths = PATHS[name] ?? PATHS.file
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      fill={filled ? 'currentColor' : 'none'}
      stroke={filled ? 'none' : 'currentColor'}
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths.map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  )
}

export function Stars({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <span className="inline-flex items-center gap-0.5 text-[#00B67A]" aria-hidden="true">
      {[0, 1, 2, 3, 4].map((i) => (
        <Icon key={i} name="star" filled className={className} />
      ))}
    </span>
  )
}
