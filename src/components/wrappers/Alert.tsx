import MuiAlert from '@mui/material/Alert'

interface AlertProps {
  message?: string
  severity?: 'error' | 'info' | 'success' | 'warning'
  children?: React.ReactNode
  [key: string]: unknown
}

export function Alert({ message, severity = 'info', children, ...rest }: AlertProps) {
  return (
    <MuiAlert severity={severity} {...rest}>
      {message ?? children}
    </MuiAlert>
  )
}
