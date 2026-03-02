import { Stack } from '@mui/material'

interface RowProps {
  spacing?: number
  children?: React.ReactNode
  [key: string]: unknown
}

export function Row({ spacing = 1, children, ...rest }: RowProps) {
  return (
    <Stack direction="row" spacing={spacing} {...rest}>
      {children}
    </Stack>
  )
}
