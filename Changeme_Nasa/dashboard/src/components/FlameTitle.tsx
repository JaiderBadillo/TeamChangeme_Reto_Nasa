import { useId } from 'react'

interface FlameTitleProps {
  children: string
  className?: string
}

const HOVER_SPARKS = [
  { right: '-16px', delay: '0s', duration: '1.25s', size: 3.5, drift: '-4px' },
  { right: '-30px', delay: '0.4s', duration: '1.5s', size: 2.5, drift: '6px' },
  { right: '-22px', delay: '0.8s', duration: '1.15s', size: 3, drift: '2px' },
]

export function FlameTitle({ children, className = '' }: FlameTitleProps) {
  const uid = useId().replace(/:/g, '')
  const glowFilter = `flame-glow-${uid}`
  const outerGrad = `flame-outer-${uid}`
  const midGrad = `flame-mid-${uid}`
  const coreGrad = `flame-core-${uid}`

  return (
    <div className={`flex justify-center ${className}`}>
      <div
        tabIndex={0}
        className="flame-title-trigger relative inline-flex items-center justify-center cursor-default focus:outline-none"
      >
        <h1 className="svg-page-title text-center">{children}</h1>

        {/* Hover-only glowing S-wave incandescent flame ("llamita") */}
        <span
          aria-hidden="true"
          className="flame-hover-badge pointer-events-none absolute -right-11 md:-right-13 -top-1.5 flex items-center justify-center"
        >
          <svg viewBox="0 0 48 58" className="w-9 h-11 md:w-11 md:h-[54px] overflow-visible">
            <defs>
              <filter id={glowFilter} x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <linearGradient id={outerGrad} x1="20%" y1="100%" x2="75%" y2="0%">
                <stop offset="0%" stopColor="#D13B1F" />
                <stop offset="55%" stopColor="#F27756" />
                <stop offset="100%" stopColor="#FEB352" />
              </linearGradient>
              <linearGradient id={midGrad} x1="30%" y1="100%" x2="60%" y2="0%">
                <stop offset="0%" stopColor="#F27756" />
                <stop offset="55%" stopColor="#FEB352" />
                <stop offset="100%" stopColor="#FFE694" />
              </linearGradient>
              <linearGradient id={coreGrad} x1="50%" y1="100%" x2="50%" y2="0%">
                <stop offset="0%" stopColor="#FFE18C" />
                <stop offset="55%" stopColor="#FFF4CC" />
                <stop offset="100%" stopColor="#FFFFFF" />
              </linearGradient>
            </defs>

            {/* Ambient firelight halo */}
            <ellipse
              cx="24"
              cy="36"
              rx="14"
              ry="15"
              fill="#F27756"
              opacity="0.24"
              filter={`url(#${glowFilter})`}
            />

            {/* Layer 1: Graceful S-wave crimson-orange outer flame */}
            <path
              className="flame-layer-outer"
              filter={`url(#${glowFilter})`}
              d="M24 52 C14 52 9 44 10 34 C10.8 26 16 21 15.5 13 C18.5 16.5 19.5 21 19 23 C21 14 25.5 9 24.5 3 C29 9 31.5 16 29.5 24 C32.5 21.5 35.5 19 36.5 15.5 C38 22 39 28 38 35 C37 45 32 52 24 52 Z"
              fill={`url(#${outerGrad})`}
            />

            {/* Layer 2: Inner golden-amber tongue swaying independently */}
            <path
              className="flame-layer-mid"
              d="M24 50 C17 50 13.5 44 14 36.5 C14.5 30 18.5 26 20 20 C21 22.5 21.5 24.5 21.5 26 C23 19.5 25.5 16.5 26 12 C28.5 17.5 29.5 23 28 29 C30 27.5 31.5 26 32.5 23.5 C34 29 34 36 33 41 C31.5 47 28.5 50 24 50 Z"
              fill={`url(#${midGrad})`}
            />

            {/* Layer 3: Soft white-gold incandescent core */}
            <path
              className="flame-layer-core"
              d="M24 48 C19.8 48 17.5 44 18 39 C18.5 34.5 21.5 31.5 23.5 26.5 C25.5 30.5 29.5 34.5 29.5 39.5 C29.5 44.5 27.5 48 24 48 Z"
              fill={`url(#${coreGrad})`}
              opacity="0.96"
            />

            {/* Pinched-off detached flame droplet */}
            <circle cx="30" cy="6" r="1.7" fill="#FEB352" className="flame-pinch-dot" />
          </svg>
        </span>

        {/* Delicate sparks rising only while hovered */}
        {HOVER_SPARKS.map((e, i) => (
          <span
            key={i}
            aria-hidden="true"
            className="flame-hover-ember pointer-events-none"
            style={
              {
                right: e.right,
                width: `${e.size}px`,
                height: `${e.size}px`,
                animationDelay: e.delay,
                animationDuration: e.duration,
                '--ember-drift': e.drift,
                background: '#FEB352',
                boxShadow: '0 0 8px rgba(254, 179, 82, 0.95)',
              } as React.CSSProperties
            }
          />
        ))}
      </div>
    </div>
  )
}
