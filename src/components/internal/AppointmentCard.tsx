import { Card, CardContent, Chip, Stack, Typography } from '@mui/material'
import BusinessIcon from '@mui/icons-material/Business'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'

const STATUS_CONFIG: Record<
  string,
  { color: 'success' | 'warning' | 'error'; icon?: React.ReactNode; variant: 'filled' | 'outlined' }
> = {
  valid: { color: 'success', icon: <CheckCircleIcon sx={{ fontSize: 14 }} />, variant: 'filled' },
  Valid: { color: 'success', icon: <CheckCircleIcon sx={{ fontSize: 14 }} />, variant: 'filled' },
  expiring: { color: 'warning', icon: <CancelIcon sx={{ fontSize: 14 }} />, variant: 'filled' },
  Expiring: { color: 'warning', icon: <CancelIcon sx={{ fontSize: 14 }} />, variant: 'filled' },
  invalid: { color: 'error', icon: <CancelIcon sx={{ fontSize: 14 }} />, variant: 'filled' },
  Invalid: { color: 'error', icon: <CancelIcon sx={{ fontSize: 14 }} />, variant: 'filled' },
  'high no-show': { color: 'warning', variant: 'filled' },
  'High No-Show': { color: 'warning', variant: 'filled' },
}

interface AppointmentCardProps {
  patient?: string
  doctor?: string
  insurance?: string
  datetime?: string
  status?: string
  statuses?: string[]
  onClick?: () => void
  [key: string]: unknown
}

export function AppointmentCard({
  patient,
  doctor,
  insurance,
  datetime,
  status,
  statuses,
  onClick,
  ...rest
}: AppointmentCardProps) {
  const statusList = statuses ?? (status ? [status] : [])
  const isInvalid = statusList.some((s) => s?.toLowerCase() === 'invalid')
  const isHighNoShow = statusList.some((s) => s?.toLowerCase().includes('no-show'))

  const cardBg = isInvalid ? 'rgba(211, 47, 47, 0.08)' : isHighNoShow ? 'rgba(237, 108, 2, 0.08)' : undefined

  return (
    <Card
      variant="outlined"
      onClick={onClick}
      sx={{
        cursor: onClick ? 'pointer' : undefined,
        bgcolor: cardBg,
        '&:hover': onClick ? { bgcolor: 'action.hover' } : undefined,
      }}
      {...rest}
    >
      <CardContent sx={{ py: 1.25, px: 1.5, '&:last-child': { pb: 1.25 } }}>
        <Stack spacing={0.5}>
          {patient && (
            <Typography variant="subtitle2" fontWeight={700}>
              {patient}
            </Typography>
          )}
          {doctor && (
            <Typography variant="body2" color="text.secondary">
              {doctor}
            </Typography>
          )}
          {insurance && (
            <Stack direction="row" spacing={0.5} alignItems="center">
              <BusinessIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {insurance}
              </Typography>
            </Stack>
          )}
          {datetime && (
            <Stack direction="row" spacing={0.5} alignItems="center">
              <CalendarMonthIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {datetime}
              </Typography>
            </Stack>
          )}
          {statusList.length > 0 && (
            <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mt: 0.75 }}>
              {statusList.map((s, i) => {
                const config = STATUS_CONFIG[s] ?? { color: 'default' as const, variant: 'outlined' as const }
                const chipProps = config.icon
                  ? { icon: config.icon as React.ReactElement }
                  : {}
                return (
                  <Chip
                    key={i}
                    label={s}
                    size="small"
                    color={config.color}
                    variant={config.variant}
                    {...chipProps}
                    sx={{ height: 22, '& .MuiChip-icon': { ml: 0.5 } }}
                  />
                )
              })}
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  )
}
