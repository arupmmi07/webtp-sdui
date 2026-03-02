import { Box } from '@mui/material'
import { Header } from './Header'
import { StaticSection } from '@/components/demo/StaticSection'
import { useDemo } from '@/context/DemoContext'

const CONTENT_MAX_WIDTH = 1200

interface AppShellProps {
  children: React.ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const { showAnnotations } = useDemo()

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.100' }}>
      <Box
        sx={{
          maxWidth: CONTENT_MAX_WIDTH,
          width: '100%',
          mx: 'auto',
          minHeight: 'fit-content',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: '#fff',
          boxShadow: '0 0 0 1px rgba(0,0,0,0.04)',
        }}
      >
        <StaticSection label="Static" showAnnotation={showAnnotations}>
          <Header />
        </StaticSection>
        <Box component="main" sx={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
          {children}
        </Box>
      </Box>
    </Box>
  )
}
