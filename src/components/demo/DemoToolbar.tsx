import { useState } from 'react'
import { Box, IconButton, Tooltip, Collapse, Typography, Button, Stack } from '@mui/material'
import ScienceIcon from '@mui/icons-material/Science'
import LabelIcon from '@mui/icons-material/Label'
import CategoryIcon from '@mui/icons-material/Category'
import CloudDownloadIcon from '@mui/icons-material/CloudDownload'
import CloseIcon from '@mui/icons-material/Close'
import { useDemo } from '@/context/DemoContext'
import { SpecLoaderDialog } from './SpecLoaderDialog'

export function DemoToolbar() {
  const { showAnnotations, showComponentSource, setShowAnnotations, setShowComponentSource } = useDemo()
  const [expanded, setExpanded] = useState(false)
  const [showSpecLoader, setShowSpecLoader] = useState(false)

  return (
    <>
      <Box
        sx={{
          position: 'fixed',
          bottom: 32,
          right: 32,
          zIndex: 1300,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: 1,
        }}
      >
        <Collapse in={expanded}>
          <Box
            sx={{
              bgcolor: 'background.paper',
              borderRadius: 2,
              boxShadow: 3,
              p: 2,
              mb: 1,
              minWidth: 280,
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Demo Mode
              </Typography>
              <IconButton size="small" onClick={() => setExpanded(false)}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Stack>
            <Stack spacing={1}>
              <Button
                size="small"
                variant={showAnnotations ? 'contained' : 'outlined'}
                startIcon={<LabelIcon />}
                onClick={() => setShowAnnotations(!showAnnotations)}
                fullWidth
              >
                {showAnnotations ? 'Hide' : 'Show'} SDUI vs Static
              </Button>
              <Button
                size="small"
                variant={showComponentSource ? 'contained' : 'outlined'}
                startIcon={<CategoryIcon />}
                onClick={() => setShowComponentSource(!showComponentSource)}
                fullWidth
              >
                {showComponentSource ? 'Hide' : 'Show'} Component Source
              </Button>
              <Button
                size="small"
                variant="outlined"
                startIcon={<CloudDownloadIcon />}
                onClick={() => setShowSpecLoader(true)}
                fullWidth
              >
                Load New Spec (No Redeploy)
              </Button>
            </Stack>
          </Box>
        </Collapse>
        <Tooltip title="Demo mode: Show SDUI vs Static, load specs">
          <IconButton
            onClick={() => setExpanded(!expanded)}
            sx={{
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              width: 48,
              height: 48,
              boxShadow: 3,
              '&:hover': { bgcolor: 'primary.dark' },
            }}
          >
            <ScienceIcon />
          </IconButton>
        </Tooltip>
      </Box>
      <SpecLoaderDialog open={showSpecLoader} onClose={() => setShowSpecLoader(false)} />
    </>
  )
}
