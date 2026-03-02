import { Stack, Typography } from '@mui/material'
import MuiDivider from '@mui/material/Divider'

export interface SummaryStatItem {
  label: string
  value: string
  onClick?: () => void
  valueFirst?: boolean
  [key: string]: unknown
}

interface SummaryStatProps {
  items?: SummaryStatItem[]
  spacing?: number
  valueFirst?: boolean
  inverted?: boolean
  [key: string]: unknown
}

function StatItem({
  label,
  value,
  onClick,
  valueFirst,
  inverted,
}: SummaryStatItem & { inverted?: boolean }) {
  const secondaryColor = inverted ? 'rgba(255,255,255,0.85)' : 'text.secondary'
  const inner = valueFirst ? (
    <>
      <Typography component="span" variant="body2" fontWeight={600} sx={inverted ? { color: 'inherit' } : undefined}>
        {value}
      </Typography>
      <Typography
        component="span"
        variant="body2"
        color={!inverted ? 'text.secondary' : undefined}
        sx={{ ml: 0.5, ...(inverted ? { color: secondaryColor } : {}) }}
      >
        {label}
      </Typography>
    </>
  ) : (
    <>
      <Typography
        component="span"
        variant="body2"
        color={!inverted ? 'text.secondary' : undefined}
        sx={{ ...(inverted ? { color: secondaryColor } : {}), ...(onClick ? { mr: 0.5 } : {}) }}
      >
        {label}
      </Typography>
      <Typography component="span" variant="body2" fontWeight={500} sx={inverted ? { color: 'inherit' } : undefined}>
        {value}
      </Typography>
    </>
  )

  if (onClick) {
    return (
      <Typography
        component="button"
        variant="body2"
        onClick={onClick}
        sx={{
          border: 'none',
          background: 'none',
          cursor: 'pointer',
          padding: 0,
          font: 'inherit',
          color: 'inherit',
          display: 'inline-flex',
          alignItems: 'baseline',
          gap: 0.5,
          '&:hover': { textDecoration: 'underline' },
        }}
      >
        {inner}
      </Typography>
    )
  }

  return (
    <Stack direction="row" spacing={0.5} alignItems="baseline" sx={{ flexShrink: 0 }}>
      {inner}
    </Stack>
  )
}

export function SummaryStat({ items = [], spacing = 1, valueFirst = false, inverted = false, ...rest }: SummaryStatProps) {
  if (items.length === 0) return null

  return (
    <Stack direction="row" spacing={spacing} alignItems="center" flexWrap="wrap" useFlexGap {...rest}>
      {items.map((item, idx) => (
        <Stack key={idx} direction="row" alignItems="center" spacing={spacing}>
          {idx > 0 && (
            <MuiDivider
              orientation="vertical"
              flexItem
              sx={{ mx: 0.5, borderColor: inverted ? 'rgba(255,255,255,0.4)' : undefined }}
            />
          )}
          <StatItem {...item} valueFirst={valueFirst ?? item.valueFirst} inverted={inverted} />
        </Stack>
      ))}
    </Stack>
  )
}
