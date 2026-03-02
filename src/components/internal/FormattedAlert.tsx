import MuiAlert from '@mui/material/Alert'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import { FormattedText } from './FormattedText'

export interface FormattedPart {
  text: string
  bold?: boolean
}

interface FormattedAlertProps {
  parts?: FormattedPart[]
  message?: string
  severity?: 'error' | 'info' | 'success' | 'warning'
  icon?: boolean
  [key: string]: unknown
}

export function FormattedAlert({ parts = [], message, severity = 'info', icon = true, ...rest }: FormattedAlertProps) {
  const content = parts.length > 0 ? <FormattedText parts={parts} variant="body2" /> : (message ?? null)
  if (!content) return null

  return (
    <MuiAlert
      severity={severity}
      icon={icon ? undefined : false}
      iconMapping={severity === 'info' ? { info: <InfoOutlinedIcon fontSize="inherit" /> } : undefined}
      {...rest}
    >
      {content}
    </MuiAlert>
  )
}
