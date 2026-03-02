import { useState } from 'react'
import ToggleButton from '@mui/material/ToggleButton'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import { Box, Typography } from '@mui/material'

export interface SegmentedOption {
  value: string
  label?: string
}

type OptionInput = string | SegmentedOption

interface SegmentedControlProps {
  options?: OptionInput[]
  value?: string
  onChange?: (value: string) => void
  variant?: 'buttons' | 'text'
  [key: string]: unknown
}

function normalizeOption(opt: OptionInput): { value: string; label: string } {
  return typeof opt === 'string' ? { value: opt, label: opt } : { value: opt.value, label: opt.label ?? opt.value }
}

export function SegmentedControl({
  options = [],
  value: controlledValue,
  onChange,
  variant = 'buttons',
  ...rest
}: SegmentedControlProps) {
  const normalizedOptions = options.map(normalizeOption)
  const [internalValue, setInternalValue] = useState(normalizedOptions[0]?.value ?? '')
  const value = controlledValue ?? internalValue
  const isControlled = controlledValue !== undefined

  const handleChange = (newValue: string) => {
    if (!isControlled) {
      setInternalValue(newValue)
    }
    onChange?.(newValue)
  }

  if (variant === 'text') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }} {...rest}>
        {normalizedOptions.map((opt, idx) => (
          <Box key={opt.value} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {idx > 0 && (
              <Typography component="span" variant="body2" color="text.secondary" sx={{ px: 0.25 }}>
                |
              </Typography>
            )}
            <Typography
              component="button"
              variant="body2"
              onClick={() => handleChange(opt.value)}
              sx={{
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                padding: 0,
                font: 'inherit',
                color: value === opt.value ? 'primary.main' : 'text.secondary',
                fontWeight: value === opt.value ? 600 : 400,
                textDecoration: value === opt.value ? 'underline' : 'none',
                textUnderlineOffset: 4,
                '&:hover': { color: 'primary.main', textDecoration: 'underline' },
              }}
            >
              {opt.label}
            </Typography>
          </Box>
        ))}
      </Box>
    )
  }

  const handleToggleChange = (_: React.MouseEvent<HTMLElement>, newValue: string | null) => {
    if (newValue === null) return
    handleChange(newValue)
  }

  return (
    <ToggleButtonGroup value={value} exclusive onChange={handleToggleChange} size="small" {...rest}>
      {normalizedOptions.map((opt) => (
        <ToggleButton key={opt.value} value={opt.value}>
          {opt.label}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  )
}
