import { useState, useEffect } from 'react'
import { Box, IconButton, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import type { FlowId } from '@/context/Flow4ChatContext'

const FLOW1_TIPS: Record<number, string> = {
  0: "Type **Hi**, **Hello**, or **Show me my day** in the Search/Ask bar below and press Enter to start.",
  1: "Click **Show Me Pending Referrals** to view the referral form.",
  2: "Select **Form not legible** in the dropdown to request a revised form.",
  3: "Click the **mail icon** to send the message.",
  4: "Review the confirmation. Click **Continue** or next action to proceed.",
  5: "You're almost done. Proceed to the scheduler view.",
  6: "Switch between **Doctor View** and **Front Desk View** using the toggle above.",
}

const FLOW2_TIPS: Record<number, string> = {
  0: "Type **Hi**, **Hello**, or **Show me my day** in the Search/Ask bar below and press Enter to start.",
  1: "Click **5 Referrals in Queue** or any option to continue.",
  2: "Follow the on-screen actions to proceed.",
  3: "Continue through the flow steps.",
  4: "Continue through the flow steps.",
  5: "Continue through the flow steps.",
  6: "Continue through the flow steps.",
  7: "You've completed Flow 2.",
}

function parseTip(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((p, i) => {
    if (p.startsWith('**') && p.endsWith('**')) {
      return <strong key={i}>{p.slice(2, -2)}</strong>
    }
    return p
  })
}

interface DemoTipsProps {
  flowId?: FlowId
  step?: number
  /** When true, show home page tip */
  home?: boolean
}

const HOME_TIP = "Click **START FLOW1** or **START FLOW2** to begin the demo. Each flow simulates a different use case."

export function DemoTips({ flowId = 'flow1', step = 0, home }: DemoTipsProps) {
  const [dismissed, setDismissed] = useState(false)
  const tips = flowId === 'flow1' ? FLOW1_TIPS : FLOW2_TIPS
  const tip = home ? HOME_TIP : tips[step]

  useEffect(() => {
    setDismissed(false)
  }, [step, home])

  if (!tip || dismissed) return null

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 80,
        right: 16,
        zIndex: 1200,
        maxWidth: 280,
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 3,
        border: '1px solid',
        borderColor: 'primary.main',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 1.5,
          py: 1,
          bgcolor: 'primary.light',
          color: 'primary.contrastText',
        }}
      >
        <LightbulbIcon sx={{ fontSize: 18 }} />
        <Typography variant="caption" fontWeight={600} sx={{ flex: 1 }}>
          {home ? 'Get Started' : `Step ${step} · ${flowId === 'flow1' ? 'Flow 1' : 'Flow 2'}`}
        </Typography>
        <IconButton size="small" onClick={() => setDismissed(true)} sx={{ color: 'inherit', p: 0.25 }}>
          <CloseIcon sx={{ fontSize: 16 }} />
        </IconButton>
      </Box>
      <Box sx={{ px: 1.5, py: 1.5 }}>
        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>
          {parseTip(tip)}
        </Typography>
      </Box>
    </Box>
  )
}
