import { Box, Stack } from '@mui/material'
import { WeeklyHeader } from './WeeklyHeader'
import { AppointmentCard } from './AppointmentCard'

export interface AppointmentItem {
  patient?: string
  doctor?: string
  insurance?: string
  datetime?: string
  status?: string
  onClick?: () => void
  [key: string]: unknown
}

export interface WeekGroup {
  dateRange: string
  count: number
  appointments: AppointmentItem[]
}

interface WeeklyAppointmentsViewProps {
  weeks?: WeekGroup[]
  minColumnWidth?: number
  [key: string]: unknown
}

export function WeeklyAppointmentsView({
  weeks = [],
  minColumnWidth = 280,
  ...rest
}: WeeklyAppointmentsViewProps) {
  if (weeks.length === 0) return null

  return (
    <Box
      sx={{
        overflowX: 'auto',
        overflowY: 'auto',
        pb: 1,
        '&::-webkit-scrollbar': { height: 8 },
        '&::-webkit-scrollbar-thumb': { bgcolor: 'grey.400', borderRadius: 4 },
      }}
      {...rest}
    >
      <Stack direction="row" spacing={2} alignItems="flex-start" sx={{ minWidth: 'min-content', pr: 2 }}>
        {weeks.map((week, weekIdx) => (
          <Stack
            key={weekIdx}
            direction="column"
            spacing={1.5}
            sx={{
              minWidth: minColumnWidth,
              flexShrink: 0,
            }}
          >
            <Box
              sx={{
                bgcolor: 'grey.50',
                borderRadius: 1,
                px: 1.5,
                py: 1,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <WeeklyHeader
                dateRange={week.dateRange}
                count={week.count}
                showIcon
                countFormat="parentheses"
              />
            </Box>
            <Stack direction="column" spacing={1}>
              {week.appointments.map((apt, aptIdx) => (
                <AppointmentCard key={aptIdx} {...apt} />
              ))}
            </Stack>
          </Stack>
        ))}
      </Stack>
    </Box>
  )
}
