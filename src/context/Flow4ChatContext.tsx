import { createContext, useContext, useCallback, useState, useMemo } from 'react'
import { ActionContext } from '@/renderer/ActionContext'
import flow1Step1 from '@/views/flow1/delta-step1.json'
import flow1Step2 from '@/views/flow1/delta-step2.json'
import flow1Step3 from '@/views/flow1/delta-step3.json'
import flow1Step4 from '@/views/flow1/delta-step4.json'
import flow1Step5 from '@/views/flow1/delta-step5.json'
import flow2Step1 from '@/views/flow2/delta-step1.json'
import flow2Step2 from '@/views/flow2/delta-step2.json'
import flow2Step3 from '@/views/flow2/delta-step3.json'
import flow2Step4 from '@/views/flow2/delta-step4.json'
import flow2Step5 from '@/views/flow2/delta-step5.json'
import flow2Step6 from '@/views/flow2/delta-step6.json'
import flow2Step7 from '@/views/flow2/delta-step7.json'
import doctorScheduler from '@/views/flow1/scheduler/doctor-scheduler.json'
import frontDeskScheduler from '@/views/flow1/scheduler/front-desk-scheduler.json'

export type FlowId = 'flow1' | 'flow2'

/** Delta JSONs per flow: each step is the next conversation message */
const FLOW_DELTAS: Record<FlowId, Record<number, unknown>> = {
  flow1: {
    1: flow1Step1,
    2: flow1Step2,
    3: flow1Step3,
    4: flow1Step4,
    5: flow1Step5,
  },
  flow2: {
    1: flow2Step1,
    2: flow2Step2,
    3: flow2Step3,
    4: flow2Step4,
    5: flow2Step5,
    6: flow2Step6,
    7: flow2Step7,
  },
}

const SCHEDULER_SPECS = {
  doctor: doctorScheduler,
  'front-desk': frontDeskScheduler,
} as const

export type SchedulerRole = keyof typeof SCHEDULER_SPECS

function toNodes(delta: unknown): unknown[] {
  if (Array.isArray(delta)) return delta
  if (delta != null && typeof delta === 'object' && 'type' in (delta as object)) return [delta]
  return []
}

function buildChatSpec(flowId: FlowId, throughStep: number, schedulerRole: SchedulerRole): unknown {
  // Step 0: blank chat — no message to render
  if (throughStep === 0) {
    return { type: 'Column', props: { spacing: 2, style: { maxWidth: 720 } }, children: [] }
  }
  const deltas = FLOW_DELTAS[flowId]
  const step1 = deltas[1]
  if (!step1 || throughStep === 1) return step1
  const children: unknown[] = []
  for (let i = 1; i <= throughStep; i++) {
    const delta = deltas[i]
    if (delta) children.push(...toNodes(delta))
  }
  // Flow1 step 6: append scheduler as new message in chat
  if (flowId === 'flow1' && throughStep === 6) {
    const schedulerSpec = SCHEDULER_SPECS[schedulerRole]
    if (schedulerSpec && typeof schedulerSpec === 'object' && 'type' in (schedulerSpec as object)) {
      children.push(schedulerSpec)
    }
  }
  return { type: 'Column', props: { spacing: 2, style: { maxWidth: 720 } }, children }
}

/** Intercept navigate to these — advance step instead of leaving chat */
const STAY_ON_CHAT_TARGETS = ['/screen/2', '/screen/3', '/screen/4', '/screen/5', '/screen/6', '/screen/7']

const Flow4ChatContext = createContext<{
  flowId: FlowId
  step: number
  spec: unknown
  schedulerRole: SchedulerRole
  setSchedulerRole: (r: SchedulerRole) => void
  initiateChat: () => void
} | null>(null)

export function useFlow4Chat() {
  return useContext(Flow4ChatContext)
}

export function Flow4ChatProvider({
  children,
  parentExecute,
  flowId = 'flow1',
  initialStep = 1,
  schedulerRole: initialSchedulerRole = 'doctor',
}: {
  children: React.ReactNode
  parentExecute: (action: Record<string, unknown>) => void
  flowId?: FlowId
  initialStep?: number
  schedulerRole?: SchedulerRole
}) {
  const [step, setStep] = useState(initialStep)
  const [schedulerRole, setSchedulerRole] = useState<SchedulerRole>(initialSchedulerRole)
  const initiateChat = useCallback(() => setStep(1), [])

  const spec = useMemo(
    () => buildChatSpec(flowId, step, schedulerRole),
    [flowId, step, schedulerRole]
  )

  const execute = useCallback(
    (action: Record<string, unknown>) => {
      if (action?.type === 'navigate' && typeof action.to === 'string') {
        if (STAY_ON_CHAT_TARGETS.includes(action.to)) {
          const targetStep = Number(action.to.replace('/screen/', ''))
          if (!Number.isNaN(targetStep) && targetStep > step) {
            setStep(targetStep)
            return
          }
        }
      }
      parentExecute(action)
    },
    [parentExecute, step]
  )

  const value = useMemo(
    () => ({ flowId, step, spec, schedulerRole, setSchedulerRole, initiateChat }),
    [flowId, step, spec, schedulerRole, initiateChat]
  )

  return (
    <Flow4ChatContext.Provider value={value}>
      <ActionContext.Provider value={execute}>{children}</ActionContext.Provider>
    </Flow4ChatContext.Provider>
  )
}
