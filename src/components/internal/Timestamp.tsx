import { Box, Typography } from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'

interface TimestampProps {
  value?: string
  [key: string]: unknown
}

export function Timestamp({ value = '9:36 am', ...rest }: TimestampProps) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }} {...rest}>
      <SmartToyIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
      <Typography variant="caption" color="text.secondary">
        {value}
      </Typography>
    </Box>
  )
}
