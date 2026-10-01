'use client'

import { useEffect, useRef, useState, type ReactNode } from 'react'

/**
 * Fades content in on scroll using IntersectionObserver and the `[data-reveal]`
 * rule in globals.css. Server-rendered HTML stays intact for SEO.
 */
export default function Reveal({
  children,
  delay = 0,
  className = '',
  as: Tag = 'div',
}: {
  children: ReactNode
  delay?: number
  className?: string
  as?: 'div' | 'section' | 'li' | 'article'
}) {
  const ref = useRef<HTMLElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    // Anchor navigation (and headless capture) must never leave content hidden.
    const revealIfJumped = () => {
      if (window.location.hash) setVisible(true)
    }
    revealIfJumped()
    window.addEventListener('hashchange', revealIfJumped)

    if (typeof IntersectionObserver === 'undefined') {
      setVisible(true)
      return () => window.removeEventListener('hashchange', revealIfJumped)
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true)
            observer.unobserve(entry.target)
          }
        })
      },
      { rootMargin: '0px 0px -10% 0px', threshold: 0.12 },
    )
    observer.observe(node)

    // Safety net: nothing stays invisible for more than a few seconds.
    const failsafe = setTimeout(() => setVisible(true), 5000)

    return () => {
      observer.disconnect()
      clearTimeout(failsafe)
      window.removeEventListener('hashchange', revealIfJumped)
    }
  }, [])

  return (
    <Tag
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ref={ref as any}
      data-reveal=""
      className={`${visible ? 'in-view' : ''} ${className}`}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </Tag>
  )
}
