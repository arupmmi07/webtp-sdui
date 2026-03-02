import MuiButton from '@mui/material/Button'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'

const END_ICON_MAP: Record<string, React.ReactNode> = {
  expand: <ExpandMoreIcon />,
  'expand-more': <ExpandMoreIcon />,
}

interface ButtonProps {
  label?: string
  variant?: 'text' | 'outlined' | 'contained'
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'
  endIcon?: string
  children?: React.ReactNode
  [key: string]: unknown
}

export function Button({ label, variant = 'contained', color = 'primary', endIcon, children, ...rest }: ButtonProps) {
  const resolvedEndIcon = typeof endIcon === 'string' ? END_ICON_MAP[endIcon.toLowerCase()] ?? undefined : undefined
  return (
    <MuiButton variant={variant} color={color} endIcon={resolvedEndIcon} {...rest}>
      {label ?? children}
    </MuiButton>
  )
}
