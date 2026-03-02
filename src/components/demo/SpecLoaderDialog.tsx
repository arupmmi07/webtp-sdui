import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Alert,
  Chip,
  Stack,
} from '@mui/material'
import { useDemo } from '@/context/DemoContext'
import screen1Card from '@/views/sample/screen-1-card-layout.json'
import screen1Compact from '@/views/sample/screen-1-compact-stats.json'
import screen2Row from '@/views/sample/screen-2-row-cards.json'
import screen2Alert from '@/views/sample/screen-2-alert-focus.json'
import screen2Flow1 from '@/views/sample/screen2-flow1.json'
import screen3Card from '@/views/sample/screen-3-card-message.json'
import screen3Split from '@/views/sample/screen-3-split-layout.json'
import screen3Flow1 from '@/views/sample/screen3-flow1.json'
import screen4Status from '@/views/sample/screen-4-status-success.json'
import screen4Card from '@/views/sample/screen-4-card-success.json'
import screen4Flow1 from '@/views/sample/screen4-flow1.json'
import screen5Message from '@/views/sample/screen-5-message-summary.json'
import screen5Completion from '@/views/sample/screen-5-completion-card.json'
import screen6Simple from '@/views/sample/screen-6-simple-weekly.json'
import screen6Cards from '@/views/sample/screen-6-cards-summary.json'

const SAMPLE_SPECS: { label: string; spec: unknown }[] = [
  { label: 'S1: Card layout', spec: screen1Card },
  { label: 'S1: Compact stats', spec: screen1Compact },
  { label: 'S2: Row cards', spec: screen2Row },
  { label: 'S2: Alert focus', spec: screen2Alert },
  { label: 'S2: Flow 1 (chat)', spec: screen2Flow1 },
  { label: 'S3: Card message', spec: screen3Card },
  { label: 'S3: Split layout', spec: screen3Split },
  { label: 'S3: Flow 1 (referral form)', spec: screen3Flow1 },
  { label: 'S4: Status success', spec: screen4Status },
  { label: 'S4: Card success', spec: screen4Card },
  { label: 'S4: Flow 1 (form + message)', spec: screen4Flow1 },
  { label: 'S5: Message summary', spec: screen5Message },
  { label: 'S5: Completion card', spec: screen5Completion },
  { label: 'S6: Simple weekly', spec: screen6Simple },
  { label: 'S6: Cards summary', spec: screen6Cards },
]

interface SpecLoaderDialogProps {
  open: boolean
  onClose: () => void
}

export function SpecLoaderDialog({ open, onClose }: SpecLoaderDialogProps) {
  const { setLoadedSpec, clearLoadedSpec } = useDemo()
  const [url, setUrl] = useState('')
  const [jsonInput, setJsonInput] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleLoadFromUrl = async () => {
    if (!url.trim()) return
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(url.trim())
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const spec = await res.json()
      setLoadedSpec(spec)
      onClose()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }

  const handleLoadFromJson = () => {
    if (!jsonInput.trim()) return
    setError(null)
    try {
      const spec = JSON.parse(jsonInput)
      setLoadedSpec(spec)
      onClose()
    } catch {
      setError('Invalid JSON')
    }
  }

  const handleClear = () => {
    clearLoadedSpec()
    onClose()
  }

  const handleLoadSample = (spec: unknown) => {
    setLoadedSpec(spec)
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Load New Spec (No Redeploy)</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Add or change UI without redeploying the app. Pick a sample, load from URL, or paste JSON.
        </Typography>
        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
          Sample specs (2 per screen)
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mb: 2 }}>
          {SAMPLE_SPECS.map((s, i) => (
            <Chip
              key={i}
              label={s.label}
              size="small"
              onClick={() => handleLoadSample(s.spec)}
              sx={{ cursor: 'pointer' }}
            />
          ))}
        </Stack>
        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
          Load from URL
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Spec URL"
            placeholder="https://example.com/spec.json"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            size="small"
            fullWidth
          />
          <Button variant="outlined" onClick={handleLoadFromUrl} disabled={loading || !url.trim()}>
            {loading ? 'Loading...' : 'Load from URL'}
          </Button>
          <Typography variant="body2" color="text.secondary">
            Or paste JSON spec:
          </Typography>
          <TextField
            label="JSON Spec"
            placeholder='{"type": "Column", "children": [...]}'
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            multiline
            rows={6}
            size="small"
            fullWidth
            sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}
          />
          <Button variant="outlined" onClick={handleLoadFromJson} disabled={!jsonInput.trim()}>
            Load from JSON
          </Button>
          {error && <Alert severity="error">{error}</Alert>}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClear} color="inherit">
          Clear Loaded Spec
        </Button>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}
