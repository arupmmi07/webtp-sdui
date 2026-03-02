import { useLocation, useNavigate } from 'react-router-dom'
import { useDemo } from '@/context/DemoContext'
import { useActionExecutor } from '@/renderer/ActionContext'
import { Button, Stack, Typography } from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { ScreenLayout } from '@/components/layout/ScreenLayout'
import { SegmentedControl } from '@/components/wrappers/SegmentedControl'
import { Flow4ChatProvider, useFlow4Chat, type FlowId, type SchedulerRole } from '@/context/Flow4ChatContext'

const SUMMARY_ITEMS = [
  { label: 'Due appointments', value: '28' },
  { label: 'missing authorization', value: '3' },
  { label: 'benefits expiring', value: '2' },
  { label: 'in copays to collect', value: '$1,260' },
]

function ChatContent() {
  const chat = useFlow4Chat()
  const navigate = useNavigate()
  const { loadedSpec } = useDemo()
  const spec = chat?.spec ?? { type: 'Text', props: { value: 'Loading...' } }
  const step = chat?.step ?? 2
  const isScheduler = step === 6

  const toolbar = (
    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }} flexWrap="wrap">
      {loadedSpec != null ? (
        <Typography variant="caption" sx={{ px: 1, py: 0.5, bgcolor: 'success.light', color: 'success.dark', borderRadius: 1 }}>
          Loaded spec active — use Demo to clear
        </Typography>
      ) : null}
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/')} size="small">
        Back
      </Button>
      <Typography variant="h6">Chat {chat?.flowId === 'flow2' ? '(Flow 2)' : '(Flow 1)'}</Typography>
      {isScheduler && chat && (
        <SegmentedControl
          options={[
            { value: 'doctor', label: 'Doctor View' },
            { value: 'front-desk', label: 'Front Desk View' },
          ]}
          value={chat.schedulerRole}
          onChange={(v) => chat.setSchedulerRole(v as SchedulerRole)}
        />
      )}
    </Stack>
  )

  return (
    <ScreenLayout
      spec={spec}
      toolbar={toolbar}
      summaryItems={SUMMARY_ITEMS}
      fullWidth={isScheduler}
    />
  )
}

export function ChatPage() {
  const location = useLocation()
  const parentExecute = useActionExecutor()
  const state = location.state as { flow?: FlowId; step?: number } | null
  const flowId = state?.flow ?? 'flow1'
  const initialStep = state?.step ?? 1

  return (
    <Flow4ChatProvider parentExecute={parentExecute} flowId={flowId} initialStep={initialStep}>
      <ChatContent />
    </Flow4ChatProvider>
  )
}
