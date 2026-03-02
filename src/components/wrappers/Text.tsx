import { Typography } from '@mui/material'

interface TextProps {
  value?: string
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'body1' | 'body2' | 'caption' | 'subtitle1' | 'subtitle2'
  children?: React.ReactNode
  [key: string]: unknown
}

export function Text({ value, variant = 'body1', children, ...rest }: TextProps) {
  return (
    <Typography variant={variant} {...rest}>
      {value ?? children}
    </Typography>
  )
}
