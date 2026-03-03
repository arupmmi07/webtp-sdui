import { createElement, Fragment, type ReactNode } from 'react'
import { getComponent } from './registry'
import { useActionExecutor } from './ActionContext'
import { useDemo } from '@/context/DemoContext'
import { SDUINodeWrapper } from '@/components/demo/SDUINodeWrapper'

interface SDUINode {
  type: string
  props?: Record<string, unknown>
  style?: Record<string, unknown>
  action?: Record<string, unknown>
  actions?: Record<string, Record<string, unknown>>
  children?: SDUINode[]
}

function createBindAction(execute: (action: Record<string, unknown>) => void) {
  return (action: Record<string, unknown> | undefined): (() => void) | undefined => {
    if (!action) return undefined
    return () => execute(action as Record<string, unknown>)
  }
}

function renderNode(
  node: SDUINode,
  bindAction: (a: Record<string, unknown> | undefined) => (() => void) | undefined,
  execute: (action: Record<string, unknown>) => void,
  demoOpts: { showAnnotation: boolean; showSource: boolean; isTopLevel: boolean }
): ReactNode {
  const entry = getComponent(node.type)
  if (!entry) {
    console.warn(`[SDUI] Unknown component type: ${node.type}`)
    return null
  }

  const { component: Component, source } = entry
  const props = { ...(node.props ?? {}) }

  if (node.style && Object.keys(node.style).length > 0) {
    props.sx = { ...(props.sx as object ?? {}), ...node.style }
  }

  if (node.action) {
    props.onClick = bindAction(node.action)
  }

  if (node.actions) {
    for (const [key, action] of Object.entries(node.actions)) {
      const act = action as Record<string, unknown>
      const whenValue = act?.whenValue as string | undefined
      if (key === 'onChange' && whenValue !== undefined) {
        props[key] = (value: string) => {
          if (value === whenValue) {
            execute(act)
          }
        }
      } else {
        const handler = bindAction(action)
        if (handler) props[key] = handler
      }
    }
  }

  const childOpts = { ...demoOpts, isTopLevel: false }
  const children = node.children?.map((child) => renderNode(child, bindAction, execute, childOpts)).filter(Boolean) ?? []

  const element = createElement(Component as React.ComponentType<Record<string, unknown>>, props, ...children)

  const shouldWrap = (demoOpts.showAnnotation || demoOpts.showSource) && demoOpts.isTopLevel
  if (shouldWrap) {
    return (
      <SDUINodeWrapper
        type={node.type}
        source={source}
        showAnnotation={demoOpts.showAnnotation}
        showSource={demoOpts.showSource}
      >
        {element}
      </SDUINodeWrapper>
    )
  }

  return element
}

function parseSpec(spec: unknown): SDUINode[] {
  if (Array.isArray(spec)) {
    return spec.filter((n): n is SDUINode => n != null && typeof n === 'object' && typeof (n as SDUINode).type === 'string')
  }
  if (spec != null && typeof spec === 'object' && typeof (spec as SDUINode).type === 'string') {
    return [spec as SDUINode]
  }
  return []
}

export interface SDUIRendererProps {
  spec: unknown
}

export function SDUIRenderer({ spec }: SDUIRendererProps) {
  const execute = useActionExecutor()
  const { showAnnotations, showComponentSource } = useDemo()
  const bindAction = createBindAction(execute)
  const nodes = parseSpec(spec)
  if (nodes.length === 0) {
    return null
  }

  const demoOpts = { showAnnotation: showAnnotations, showSource: showComponentSource, isTopLevel: true }

  return (
    <Fragment>
      {nodes.map((node, i) => (
        <Fragment key={i}>{renderNode(node, bindAction, execute, demoOpts)}</Fragment>
      ))}
    </Fragment>
  )
}
