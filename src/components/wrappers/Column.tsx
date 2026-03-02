import { Stack } from '@mui/material'

interface ColumnProps {
  spacing?: number
  children?: React.ReactNode
  [key: string]: unknown
}

export function Column({ spacing = 1, children, ...rest }: ColumnProps) {
  return (
    <Stack direction="column" spacing={spacing} {...rest}>
      {children}
    </Stack>
  )
}
