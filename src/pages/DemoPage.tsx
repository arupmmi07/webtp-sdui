import { useState } from 'react'
import { Box, Stack, Typography } from '@mui/material'
import { SDUIRenderer } from '@/renderer/SDUIRenderer'
import { SegmentedControl } from '@/components/wrappers/SegmentedControl'
import doctorSchedulerSpec from '@/views/flow1/scheduler/doctor-scheduler.json'
import frontDeskSchedulerSpec from '@/views/flow1/scheduler/front-desk-scheduler.json'

const SPECS = {
  doctor: doctorSchedulerSpec,
  'front-desk': frontDeskSchedulerSpec,
} as const

type Role = keyof typeof SPECS

export function DemoPage() {
  const [role, setRole] = useState<Role>('doctor')
  const spec = SPECS[role]

  return (
    <Box sx={{ p: 2, maxWidth: 1200, mx: 'auto' }}>
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
        <Typography variant="h5">SDUI Demo</Typography>
        <SegmentedControl
          options={[
            { value: 'doctor', label: 'Doctor' },
            { value: 'front-desk', label: 'Front Desk' },
          ]}
          value={role}
          onChange={(value) => setRole(value as Role)}
        />
      </Stack>
      <SDUIRenderer spec={spec} />
    </Box>
  )
}
