import { Stack, Typography } from '@mui/material'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'

interface WeeklyHeaderProps {
  dateRange?: string
  count?: number
  showIcon?: boolean
  countFormat?: 'chip' | 'parentheses'
  [key: string]: unknown
}

export function WeeklyHeader({
  dateRange = '',
  count,
  showIcon = true,
  countFormat = 'chip',
  ...rest
}: WeeklyHeaderProps) {
  const countDisplay =
    count !== undefined && count !== null
      ? countFormat === 'parentheses'
        ? ` (${count})`
        : null
      : null

  return (
    <Stack direction="row" alignItems="center" spacing={1} flexWrap="wrap" useFlexGap {...rest}>
      {showIcon && <CalendarMonthIcon color="action" fontSize="small" />}
      <Typography variant="subtitle2" fontWeight={600}>
        {dateRange}
        {countDisplay}
      </Typography>
    </Stack>
  )
}
