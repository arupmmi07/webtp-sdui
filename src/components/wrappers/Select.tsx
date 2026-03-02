import { useState } from 'react'
import FormControl from '@mui/material/FormControl'
import InputLabel from '@mui/material/InputLabel'
import MuiSelect from '@mui/material/Select'
import MenuItem from '@mui/material/MenuItem'

export interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  options?: SelectOption[]
  value?: string
  label?: string
  onChange?: (value: string) => void
  fullWidth?: boolean
  [key: string]: unknown
}

export function Select({
  options = [],
  value: controlledValue,
  label,
  onChange,
  fullWidth = true,
  selectSx,
  menuProps,
  ...rest
}: SelectProps) {
  const [internalValue, setInternalValue] = useState('')
  const value = controlledValue ?? internalValue
  const isControlled = controlledValue !== undefined

  const handleChange = (newValue: string) => {
    if (!isControlled) {
      setInternalValue(newValue)
    }
    onChange?.(newValue)
  }

  return (
    <FormControl fullWidth={fullWidth} size="small" {...rest}>
      {label && <InputLabel id="sdui-select-label">{label}</InputLabel>}
      <MuiSelect
        labelId="sdui-select-label"
        value={value}
        label={label}
        onChange={(e) => handleChange(String(e.target.value))}
        sx={selectSx ? (selectSx as object) : undefined}
        MenuProps={menuProps ? (menuProps as object) : undefined}
      >
        {options.map((opt) => (
          <MenuItem key={opt.value} value={opt.value}>
            {opt.label}
          </MenuItem>
        ))}
      </MuiSelect>
    </FormControl>
  )
}
