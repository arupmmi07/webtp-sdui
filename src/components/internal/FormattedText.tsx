import { Typography } from '@mui/material'

export interface FormattedPart {
  text: string
  bold?: boolean
}

interface FormattedTextProps {
  parts?: FormattedPart[]
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'body1' | 'body2' | 'caption' | 'subtitle1' | 'subtitle2'
  [key: string]: unknown
}

export function FormattedText({ parts = [], variant = 'body1', ...rest }: FormattedTextProps) {
  if (parts.length === 0) return null

  return (
    <Typography variant={variant} component="span" {...rest}>
      {parts.map((part, idx) =>
        part.bold ? (
          <strong key={idx}>{part.text}</strong>
        ) : (
          <span key={idx}>{part.text}</span>
        )
      )}
    </Typography>
  )
}
