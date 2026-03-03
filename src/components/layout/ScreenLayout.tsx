import { Box } from '@mui/material'
import { AppShell } from './AppShell'
import { SDUIRenderer } from '@/renderer/SDUIRenderer'
import { SearchAskSection } from './SearchAskSection'
import { StaticSection } from '@/components/demo/StaticSection'
import { useDemo } from '@/context/DemoContext'

interface ScreenLayoutProps {
  spec: unknown
  toolbar?: React.ReactNode
  summaryItems?: { label: string; value: string }[]
  fullWidth?: boolean
  onSearchSubmit?: () => void
}

export function ScreenLayout({ spec, toolbar, summaryItems, fullWidth, onSearchSubmit }: ScreenLayoutProps) {
  const { showAnnotations } = useDemo()

  return (
    <AppShell>
      <Box
        sx={{
          p: 2,
          flex: 1,
          width: '100%',
          minHeight: 0,
          ...(fullWidth ? {} : { maxWidth: 1200, mx: 'auto' }),
          bgcolor: fullWidth ? 'grey.50' : undefined,
        }}
      >
        {toolbar && (
          <StaticSection label="Static" showAnnotation={showAnnotations}>
            {toolbar}
          </StaticSection>
        )}
        <SDUIRenderer spec={spec} />
        <StaticSection label="Static" showAnnotation={showAnnotations}>
          <SearchAskSection summaryItems={summaryItems} onSearchSubmit={onSearchSubmit} />
        </StaticSection>
      </Box>
    </AppShell>
  )
}
