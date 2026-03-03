import { BrowserRouter, Routes, Route, Link, Navigate, useParams } from 'react-router-dom'
import { Button, Box, Stack, Typography, Card, CardContent } from '@mui/material'
import { ActionProvider } from '@/renderer/ActionContext'
import { DemoProvider } from '@/context/DemoContext'
import { AppShell } from '@/components/layout/AppShell'
import { ChatPage } from '@/pages/ChatPage'
import { DemoToolbar } from '@/components/demo/DemoToolbar'
import { DemoTips } from '@/components/demo/DemoTips'

function HomePage() {
  return (
    <AppShell>
      <DemoTips home />
      <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
        <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>
          SDUI Runtime Renderer — Demo
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Server-Driven UI: Render screens from JSON config at runtime. No redeploy to add or change UI.
        </Typography>

        <Stack spacing={2} sx={{ mb: 3 }}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Add UI Without Redeploy
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Use the Demo button (bottom-right) → Load New Spec. Paste JSON or load from URL. UI updates instantly.
              </Typography>
            </CardContent>
          </Card>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Library Agnostic
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Components from <strong>MUI</strong>, <strong>internal</strong>, and <strong>FullCalendar</strong>. Swap libs without changing specs.
              </Typography>
            </CardContent>
          </Card>
        </Stack>

        <Stack direction="row" spacing={2} flexWrap="wrap">
          <Button component={Link} to="/chat" state={{ flow: 'flow1', step: 0 }} variant="contained" color="primary" size="large">
            START FLOW1 (CHAT)
          </Button>
          <Button component={Link} to="/chat" state={{ flow: 'flow2', step: 0 }} variant="contained" color="primary" size="large">
            START FLOW2 (CHAT)
          </Button>
        </Stack>
      </Box>
    </AppShell>
  )
}

function ScreenRedirect() {
  const { screenId } = useParams()
  const step = screenId ? Math.min(Math.max(1, Number(screenId)), 6) : 1
  return <Navigate to="/chat" state={{ flow: 'flow1', step }} replace />
}

function AppRoutes() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/screen/:screenId" element={<ScreenRedirect />} />
        <Route path="/demo" element={<Navigate to="/chat" state={{ flow: 'flow1', step: 6 }} replace />} />
      </Routes>
      <DemoToolbar />
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <DemoProvider>
        <ActionProvider>
          <AppRoutes />
        </ActionProvider>
      </DemoProvider>
    </BrowserRouter>
  )
}

export default App
