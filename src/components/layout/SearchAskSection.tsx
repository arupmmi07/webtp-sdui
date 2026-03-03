import { useState } from 'react'
import { Box, TextField, InputAdornment, IconButton, Typography } from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import MicIcon from '@mui/icons-material/Mic'
import HistoryIcon from '@mui/icons-material/History'
import AssignmentIcon from '@mui/icons-material/Assignment'
import ViewModuleIcon from '@mui/icons-material/ViewModule'
import { SummaryStat } from '@/components/internal/SummaryStat'

const DEFAULT_SUMMARY_ITEMS = [
  { label: 'Due appointments', value: '28' },
  { label: 'missing authorization', value: '3' },
  { label: 'benefits expiring', value: '2' },
  { label: 'in copays to collect', value: '$1,260' },
]

const INITIATE_PHRASES = ['hi', 'hello', 'show me my day']

function matchesInitiatePhrase(value: string): boolean {
  const normalized = value.trim().toLowerCase()
  return INITIATE_PHRASES.some((p) => normalized === p || normalized.startsWith(p + ' ') || normalized.endsWith(' ' + p))
}

interface SearchAskSectionProps {
  summaryItems?: { label: string; value: string }[]
  moreLabel?: string
  onSearchSubmit?: () => void
}

/** Search/ask bar and Day's Summary - integrated near main content, not a footer */
export function SearchAskSection({ summaryItems = DEFAULT_SUMMARY_ITEMS, moreLabel = '+8 More', onSearchSubmit }: SearchAskSectionProps) {
  const [inputValue, setInputValue] = useState('')

  const handleSubmit = () => {
    const v = inputValue.trim()
    if (!v) return
    if (matchesInitiatePhrase(v)) {
      onSearchSubmit?.()
      setInputValue('')
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, pt: 2, mt: 2, borderTop: 1, borderColor: 'grey.200' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search or ask: Hi, Hello, Show me my day..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          variant="outlined"
          sx={{
            flex: 1,
            minWidth: 280,
            maxWidth: 500,
            '& .MuiOutlinedInput-root': {
              bgcolor: '#fff',
              borderRadius: 2,
              borderColor: 'grey.300',
              '& fieldset': { borderColor: 'grey.300' },
              '&:hover fieldset': { borderColor: 'grey.400' },
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start" sx={{ ml: 0.5 }}>
                <UploadFileIcon sx={{ fontSize: 20, color: 'primary.main' }} />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end" sx={{ mr: 0.5 }}>
                <IconButton size="small" onClick={handleSubmit} sx={{ p: 0.5 }}>
                  <MicIcon sx={{ fontSize: 20, color: 'primary.main' }} />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.25 }}>
            <IconButton
              size="small"
              sx={{
                border: '1px solid',
                borderColor: 'primary.main',
                color: 'primary.main',
                borderRadius: '50%',
                width: 40,
                height: 40,
                '&:hover': { bgcolor: 'primary.light', color: 'primary.contrastText' },
              }}
            >
              <HistoryIcon sx={{ fontSize: 20 }} />
            </IconButton>
            <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'text.secondary', fontWeight: 500 }}>
              History
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.25 }}>
            <IconButton
              size="small"
              sx={{
                border: '1px solid',
                borderColor: 'primary.main',
                color: 'primary.main',
                borderRadius: '50%',
                width: 40,
                height: 40,
                '&:hover': { bgcolor: 'primary.light', color: 'primary.contrastText' },
              }}
            >
              <AssignmentIcon sx={{ fontSize: 20 }} />
            </IconButton>
            <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'text.secondary', fontWeight: 500 }}>
              12 Tasks
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.25 }}>
            <IconButton
              size="small"
              sx={{
                border: '1px solid',
                borderColor: 'primary.main',
                color: 'primary.main',
                borderRadius: '50%',
                width: 40,
                height: 40,
                '&:hover': { bgcolor: 'primary.light', color: 'primary.contrastText' },
              }}
            >
              <ViewModuleIcon sx={{ fontSize: 20 }} />
            </IconButton>
            <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'text.secondary', fontWeight: 500 }}>
              5 Activities
            </Typography>
          </Box>
        </Box>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap', pt: 0.5 }}>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
          Day&apos;s Summary:
        </Typography>
        <SummaryStat items={summaryItems} spacing={1.5} valueFirst />
        <Typography
          component="span"
          variant="body2"
          color="primary"
          sx={{ cursor: 'pointer', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}
        >
          {moreLabel}
        </Typography>
      </Box>
    </Box>
  )
}
