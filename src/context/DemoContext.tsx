import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

export interface DemoState {
  showAnnotations: boolean
  showComponentSource: boolean
  loadedSpec?: unknown
}

interface DemoContextValue {
  showAnnotations: boolean
  showComponentSource: boolean
  loadedSpec: unknown | undefined
  setShowAnnotations: (v: boolean) => void
  setShowComponentSource: (v: boolean) => void
  setLoadedSpec: (spec: unknown) => void
  clearLoadedSpec: () => void
}

const DemoContext = createContext<DemoContextValue | null>(null)

export function DemoProvider({ children }: { children: ReactNode }) {
  const [showAnnotations, setShowAnnotations] = useState(false)
  const [showComponentSource, setShowComponentSource] = useState(false)
  const [loadedSpec, setLoadedSpecState] = useState<unknown>(undefined)

  const setLoadedSpec = useCallback((spec: unknown) => {
    setLoadedSpecState(spec)
  }, [])

  const clearLoadedSpec = useCallback(() => {
    setLoadedSpecState(undefined)
  }, [])

  return (
    <DemoContext.Provider
      value={{
        showAnnotations,
        showComponentSource,
        loadedSpec,
        setShowAnnotations,
        setShowComponentSource,
        setLoadedSpec,
        clearLoadedSpec,
      }}
    >
      {children}
    </DemoContext.Provider>
  )
}

export function useDemo() {
  const ctx = useContext(DemoContext)
  return ctx ?? { showAnnotations: false, showComponentSource: false, loadedSpec: undefined, setShowAnnotations: () => {}, setShowComponentSource: () => {}, setLoadedSpec: () => {}, clearLoadedSpec: () => {} }
}
