import { Box, Typography } from '@mui/material'

interface GreetingAvatarProps {
  greeting?: string
  [key: string]: unknown
}

/** Stylized 3D robot head: white with dark grey features, antennae, slight tilt */
function RobotAvatar() {
  return (
    <svg width="56" height="56" viewBox="0 0 56 56" fill="none" style={{ display: 'block' }}>
      <defs>
        <linearGradient id="robot-face" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FAFAFA" />
          <stop offset="100%" stopColor="#F0F0F0" />
        </linearGradient>
      </defs>
      <g transform="rotate(-4 28 28)">
        {/* Head shape */}
        <rect x="8" y="10" width="40" height="36" rx="8" fill="url(#robot-face)" stroke="#D1D5DB" strokeWidth="1" />
        {/* Antennae */}
        <line x1="22" y1="10" x2="20" y2="2" stroke="#4B5563" strokeWidth="2" strokeLinecap="round" />
        <line x1="34" y1="10" x2="36" y2="2" stroke="#4B5563" strokeWidth="2" strokeLinecap="round" />
        <circle cx="20" cy="2" r="2" fill="#4B5563" />
        <circle cx="36" cy="2" r="2" fill="#4B5563" />
        {/* Eyes */}
        <ellipse cx="22" cy="24" rx="4" ry="5" fill="#374151" />
        <ellipse cx="34" cy="24" rx="4" ry="5" fill="#374151" />
        {/* Nose - small triangle */}
        <path d="M28 30 L26 36 L30 36 Z" fill="#4B5563" />
        {/* Smile - curved line */}
        <path d="M22 42 Q28 48 34 42" stroke="#4B5563" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      </g>
    </svg>
  )
}

export function GreetingAvatar({ greeting = 'Good Morning John', ...rest }: GreetingAvatarProps) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }} {...rest}>
      <Box
        sx={{
          width: 56,
          height: 56,
          borderRadius: 2,
          bgcolor: 'grey.50',
          border: '1px solid',
          borderColor: 'grey.200',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
          transform: 'rotate(-3deg)',
          overflow: 'hidden',
        }}
      >
        <RobotAvatar />
      </Box>
      <Typography variant="h4" fontWeight={700} color="text.primary">
        {greeting}
      </Typography>
    </Box>
  )
}
