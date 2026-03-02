import MuiCard from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'

interface CardProps {
  elevation?: number
  children?: React.ReactNode
  [key: string]: unknown
}

export function Card({ elevation = 1, children, ...rest }: CardProps) {
  return (
    <MuiCard elevation={elevation} {...rest}>
      <CardContent>{children}</CardContent>
    </MuiCard>
  )
}
