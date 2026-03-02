import MuiDivider from '@mui/material/Divider'

interface DividerProps {
  [key: string]: unknown
}

export function Divider(props: DividerProps) {
  return <MuiDivider {...props} />
}
