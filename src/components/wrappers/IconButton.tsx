import MuiIconButton from '@mui/material/IconButton'
import EmailIcon from '@mui/icons-material/Email'
import ChatIcon from '@mui/icons-material/Chat'
import DescriptionIcon from '@mui/icons-material/Description'
import type { SvgIconComponent } from '@mui/icons-material'

const ICON_MAP: Record<string, SvgIconComponent> = {
  mail: EmailIcon,
  email: EmailIcon,
  chat: ChatIcon,
  document: DescriptionIcon,
  description: DescriptionIcon,
}

interface IconButtonProps {
  icon?: string
  onClick?: () => void
  [key: string]: unknown
}

export function IconButton({ icon = 'mail', onClick, ...rest }: IconButtonProps) {
  const IconComponent = ICON_MAP[icon?.toLowerCase()] ?? EmailIcon

  return (
    <MuiIconButton onClick={onClick} size="small" {...rest}>
      <IconComponent />
    </MuiIconButton>
  )
}
