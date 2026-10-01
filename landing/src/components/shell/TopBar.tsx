'use client'

import { useEffect, useState } from 'react'
import Icon from '@/components/shared/Icon'
import Logo from '@/components/shared/Logo'

const LINKS = [
  { label: 'Studio', href: '#studio' },
  { label: 'Templates', href: '#templates' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

export default function TopBar() {
  const [open, setOpen] = useState(false)
  const [stuck, setStuck] = useState(false)

  useEffect(() => {
    const onScroll = () => setStuck(window.scrollY > 6)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  return (
    <header
      className={`sticky top-0 z-50 transition-colors ${
        stuck ? 'border-b border-line bg-void/85 backdrop-blur-xl' : 'border-b border-transparent'
      }`}
    >
      <nav className="shell flex h-16 items-center justify-between gap-4">
        <a href="#top" aria-label="MyResume Studio home">
          <Logo />
        </a>

        <ul className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="font-mono text-xs uppercase tracking-[0.16em] text-dim transition-colors hover:text-pop"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-3 md:flex">
          <a
            href="#studio"
            className="btn-primary rounded-pill px-5 py-2.5 text-sm font-bold"
          >
            Paste a job
          </a>
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={open ? 'Close menu' : 'Open menu'}
          className="grid h-10 w-10 place-items-center rounded-xl border border-line text-text md:hidden"
        >
          <Icon name={open ? 'close' : 'menu'} />
        </button>
      </nav>

      {open && (
        <div className="border-t border-line bg-void md:hidden">
          <ul className="shell py-2">
            {LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block border-b border-line2 py-3.5 font-mono text-sm uppercase tracking-[0.14em] text-dim"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li className="py-4">
              <a
                href="#studio"
                className="block rounded-pill bg-pop px-5 py-3 text-center text-sm font-bold text-void"
              >
                Paste a job
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  )
}
