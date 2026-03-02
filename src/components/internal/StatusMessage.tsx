import MuiAlert from '@mui/material/Alert'

interface StatusMessageProps {
  message?: string
  severity?: 'success' | 'error' | 'warning' | 'info'
  icon?: React.ReactNode
  children?: React.ReactNode
  [key: string]: unknown
}

export function StatusMessage({
  message,
  severity = 'info',
  icon,
  children,
  ...rest
}: StatusMessageProps) {
  return (
    <MuiAlert severity={severity} icon={icon} {...rest}>
      {message ?? children}
    </MuiAlert>
  )
}
