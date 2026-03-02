interface DashboardIllustrationProps {
  width?: number
  height?: number
  [key: string]: unknown
}

export function DashboardIllustration({ width = 320, height = 280 }: DashboardIllustrationProps) {
  return (
    <svg
      viewBox="0 0 320 280"
      width={width}
      height={height}
      fill="none"
      style={{ flexShrink: 0 }}
    >
      {/* Large faint background circle */}
      <circle cx="160" cy="140" r="115" stroke="#E8EAED" strokeWidth="1.5" fill="none" />
      {/* Decorative dots and circles */}
      <circle cx="75" cy="55" r="5" fill="#E5E7EB" />
      <circle cx="250" cy="45" r="7" fill="#E5E7EB" />
      <circle cx="270" cy="175" r="4" fill="#E5E7EB" />
      <circle cx="55" cy="210" r="6" fill="#E5E7EB" />
      <circle cx="290" cy="95" r="3" fill="#E5E7EB" />
      <circle cx="35" cy="125" r="4" fill="#E5E7EB" />

      {/* Stylized leaf shapes - behind and right of character */}
      <path d="M225 85 Q248 72 262 95 Q245 102 225 85" fill="#1E3A5F" opacity={0.55} />
      <path d="M238 78 Q258 65 268 88 Q252 94 238 78" fill="#1E3A5F" opacity={0.45} />
      <path d="M250 105 Q272 98 276 122 Q258 126 250 105" fill="#1E3A5F" opacity={0.45} />

      {/* Blue form/document - to the left of character */}
      <g transform="translate(55, 115)">
        <rect x="0" y="0" width="72" height="92" rx="6" fill="#3B82F6" />
        <rect x="14" y="22" width="44" height="14" rx="3" fill="white" opacity={0.95} />
        <rect x="14" y="48" width="44" height="14" rx="3" fill="white" opacity={0.95} />
        <rect x="14" y="74" width="32" height="8" rx="2" fill="white" opacity={0.7} />
      </g>

      {/* Paper airplane - above/right of form, flying up */}
      <g transform="translate(118, 82) rotate(-25)">
        <path d="M0 2 L18 10 L0 18 L5 10 Z" fill="#1E3A5F" stroke="#1E3A5F" strokeWidth="0.5" />
      </g>

      {/* Male character - blue shirt, dark pants, pointing right hand to form */}
      <g transform="translate(155, 85)">
        {/* Head - light skin */}
        <circle cx="28" cy="18" r="16" fill="#F5D0C5" />
        {/* Eyes - friendly */}
        <ellipse cx="23" cy="17" rx="2.5" ry="2" fill="#374151" />
        <ellipse cx="33" cy="17" rx="2.5" ry="2" fill="#374151" />
        {/* Smile - open, friendly */}
        <path d="M22 24 Q28 30 34 24" stroke="#374151" strokeWidth="2" fill="none" strokeLinecap="round" />
        {/* Neck */}
        <rect x="24" y="32" width="8" height="6" fill="#F5D0C5" rx="1" />
        {/* Blue t-shirt */}
        <path d="M12 38 L44 38 L42 72 L14 72 Z" fill="#3B82F6" stroke="#2563EB" strokeWidth="0.5" />
        {/* Left arm - relaxed, with watch */}
        <path d="M12 42 L2 58 L6 60 L14 46" fill="#3B82F6" stroke="#2563EB" strokeWidth="0.5" />
        <ellipse cx="4" cy="56" rx="5" ry="4" fill="#1E3A5F" />
        {/* Right arm - pointing toward form */}
        <path d="M44 44 L58 38 L62 42 L48 48" fill="#3B82F6" stroke="#2563EB" strokeWidth="0.5" />
        <path d="M58 38 L78 22 L82 26 L62 42 Z" fill="#F5D0C5" stroke="#E5B8B0" strokeWidth="0.5" />
        {/* Dark blue pants */}
        <path d="M14 72 L18 98 L24 98 L24 72" fill="#1E3A5F" stroke="#0F172A" strokeWidth="0.5" />
        <path d="M32 72 L32 98 L38 98 L42 72" fill="#1E3A5F" stroke="#0F172A" strokeWidth="0.5" />
      </g>
    </svg>
  )
}
