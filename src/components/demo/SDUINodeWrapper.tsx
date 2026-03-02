import { Box } from '@mui/material'
import type { ComponentSource } from '@/renderer/registry'

interface SDUINodeWrapperProps {
  type: string
  source?: ComponentSource
  children: React.ReactNode
  showAnnotation?: boolean
  showSource?: boolean
}

export function SDUINodeWrapper({ type, source, children, showAnnotation, showSource }: SDUINodeWrapperProps) {
  if (!showAnnotation && !showSource) return <>{children}</>

  const badge = showSource && source ? `SDUI · ${type} (${source})` : `SDUI · ${type}`

  return (
    <Box
      sx={{
        position: 'relative',
        display: 'block',
        '&::before': {
          content: `"${badge}"`,
          position: 'absolute',
          top: 4,
          left: 4,
          fontSize: '0.65rem',
          fontWeight: 600,
          px: 0.75,
          py: 0.25,
          borderRadius: 1,
          bgcolor: 'primary.light',
          color: 'primary.contrastText',
          border: '1px solid',
          borderColor: 'primary.main',
          zIndex: 1,
          textTransform: 'uppercase',
          letterSpacing: 0.5,
          whiteSpace: 'nowrap',
        },
        '& > *': {
          outline: '1px dashed',
          outlineColor: 'primary.main',
          outlineOffset: -1,
        },
      }}
    >
      {children}
    </Box>
  )
}
