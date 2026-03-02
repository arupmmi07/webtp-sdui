import { Stack, Typography } from '@mui/material'
import PersonIcon from '@mui/icons-material/Person'
import GroupsIcon from '@mui/icons-material/Groups'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import type { SvgIconComponent } from '@mui/icons-material'

const ICON_MAP: Record<string, SvgIconComponent> = {
  person: PersonIcon,
  people: GroupsIcon,
  groups: GroupsIcon,
  calendar: CalendarMonthIcon,
}

interface IconLabelProps {
  icon?: string
  label?: string
  [key: string]: unknown
}

export function IconLabel({ icon = 'person', label = '', ...rest }: IconLabelProps) {
  const IconComponent = ICON_MAP[icon?.toLowerCase()] ?? PersonIcon
  return (
    <Stack direction="row" spacing={0.5} alignItems="center" {...rest}>
      <IconComponent sx={{ fontSize: 16, color: 'text.secondary' }} />
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
    </Stack>
  )
}
