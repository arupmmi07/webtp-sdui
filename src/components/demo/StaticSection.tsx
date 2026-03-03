import { Box } from '@mui/material'

interface StaticSectionProps {
  label?: string
  children: React.ReactNode
  showAnnotation?: boolean
}

/** Wraps static (non-SDUI) content with an optional annotation label when demo mode is on */
export function StaticSection({ label = 'Static', children, showAnnotation }: StaticSectionProps) {
  if (!showAnnotation) return <>{children}</>

  return (
    <Box
      sx={{
        position: 'relative',
        border: '2px dashed',
        borderColor: 'grey.400',
        borderRadius: 1,
        p: 0.5,
        mb: 1,
        '&::before': {
          content: `"${label}"`,
          position: 'absolute',
          top: 4,
          right: 4,
          left: 'auto',
          fontSize: '0.65rem',
          fontWeight: 600,
          px: 0.75,
          py: 0.25,
          borderRadius: 1,
          bgcolor: 'grey.100',
          color: 'grey.600',
          border: '1px dashed',
          borderColor: 'grey.400',
          zIndex: 1,
          textTransform: 'uppercase',
          letterSpacing: 0.5,
        },
      }}
    >
      {children}
    </Box>
  )
}
