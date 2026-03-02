import { createContext, useContext, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDemo } from '@/context/DemoContext'

export interface Action {
  type: string
  [key: string]: unknown
}

export const ActionContext = createContext<((action: Record<string, unknown>) => void) | null>(null)

export function useActionExecutor() {
  const execute = useContext(ActionContext)
  return execute ?? ((action: Record<string, unknown>) => console.log('[SDUI] Action:', action))
}

export function ActionProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const { clearLoadedSpec } = useDemo()

  const execute = useCallback(
    (action: Record<string, unknown>) => {
      if (action?.type === 'navigate' && typeof action.to === 'string') {
        clearLoadedSpec()
        navigate(action.to, { state: action.state ?? undefined })
        return
      }
      if (action?.type === 'emit') {
        console.log('[SDUI] Action emit:', action)
        return
      }
      console.log('[SDUI] Action:', action)
    },
    [navigate, clearLoadedSpec]
  )

  return <ActionContext.Provider value={execute}>{children}</ActionContext.Provider>
}
