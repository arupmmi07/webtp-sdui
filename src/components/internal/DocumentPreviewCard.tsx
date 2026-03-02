import { Card, CardContent, Box, IconButton } from '@mui/material'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import DownloadIcon from '@mui/icons-material/Download'
import OpenInFullIcon from '@mui/icons-material/OpenInFull'

interface DocumentPreviewCardProps {
  title?: string
  children?: React.ReactNode
  [key: string]: unknown
}

export function DocumentPreviewCard({ title, children, ...rest }: DocumentPreviewCardProps) {
  return (
    <Card variant="outlined" sx={{ overflow: 'visible', boxShadow: 1 }} {...rest}>
      <CardContent sx={{ position: 'relative', '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          {title && (
            <Box component="span" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
              {title}
            </Box>
          )}
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <IconButton size="small" color="primary">
              <DownloadIcon fontSize="small" />
            </IconButton>
            <IconButton size="small" color="primary">
              <OpenInFullIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>
        <Box
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            p: 2,
            minHeight: 200,
            bgcolor: 'grey.50',
          }}
        >
          {children}
        </Box>
        <IconButton
          size="small"
          color="primary"
          sx={{ position: 'absolute', left: -12, top: '50%', transform: 'translateY(-50%)', bgcolor: 'background.paper', border: 1, borderColor: 'divider', '&:hover': { bgcolor: 'grey.100' } }}
        >
          <ChevronLeftIcon />
        </IconButton>
        <IconButton
          size="small"
          color="primary"
          sx={{ position: 'absolute', right: -12, top: '50%', transform: 'translateY(-50%)', bgcolor: 'background.paper', border: 1, borderColor: 'divider', '&:hover': { bgcolor: 'grey.100' } }}
        >
          <ChevronRightIcon />
        </IconButton>
      </CardContent>
    </Card>
  )
}
