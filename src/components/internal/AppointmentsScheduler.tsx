import { useState } from 'react'
import { Stack } from '@mui/material'
import { SegmentedControl } from '@/components/wrappers/SegmentedControl'
import { Button } from '@/components/wrappers/Button'
import { WeeklyAppointmentsView, type WeekGroup } from './WeeklyAppointmentsView'

export type DayGroup = WeekGroup

interface AppointmentsSchedulerProps {
  weeks?: WeekGroup[]
  days?: DayGroup[]
  buttonLabel?: string
  buttonEndIcon?: string
  [key: string]: unknown
}

export function AppointmentsScheduler({
  weeks = [],
  days = [],
  buttonLabel = 'View Detailed Schedules',
  buttonEndIcon = 'expand',
  ...rest
}: AppointmentsSchedulerProps) {
  const [view, setView] = useState<'week' | 'day'>('week')
  const data = view === 'day' && days.length > 0 ? days : weeks

  return (
    <Stack spacing={2} {...rest}>
      <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between" flexWrap="wrap">
        <SegmentedControl
            options={[
              { value: 'week', label: 'Weekly View' },
              { value: 'day', label: 'Daily View' },
            ]}
            value={view}
            onChange={(v) => setView(v as 'week' | 'day')}
            variant="text"
          />
        <Button label={buttonLabel} variant="outlined" endIcon={buttonEndIcon} />
      </Stack>
      <WeeklyAppointmentsView weeks={data} />
    </Stack>
  )
}
