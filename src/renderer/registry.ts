import type { ComponentType } from 'react'
import { Text } from '@/components/wrappers/Text'
import { Button } from '@/components/wrappers/Button'
import { Card } from '@/components/wrappers/Card'
import { Alert } from '@/components/wrappers/Alert'
import { Row } from '@/components/wrappers/Row'
import { Column } from '@/components/wrappers/Column'
import { Spacer } from '@/components/wrappers/Spacer'
import { Divider } from '@/components/wrappers/Divider'
import { Select } from '@/components/wrappers/Select'
import { IconButton } from '@/components/wrappers/IconButton'
import { SegmentedControl } from '@/components/wrappers/SegmentedControl'
import { CalendarScheduler } from '@/components/wrappers/CalendarScheduler'
import { Message } from '@/components/internal/Message'
import { StatusMessage } from '@/components/internal/StatusMessage'
import { SummaryStat } from '@/components/internal/SummaryStat'
import { FormattedText } from '@/components/internal/FormattedText'
import { Timestamp } from '@/components/internal/Timestamp'
import { GreetingAvatar } from '@/components/internal/GreetingAvatar'
import { DashboardIllustration } from '@/components/internal/DashboardIllustration'
import { FormattedAlert } from '@/components/internal/FormattedAlert'
import { WeeklyHeader } from '@/components/internal/WeeklyHeader'
import { AppointmentCard } from '@/components/internal/AppointmentCard'
import { DocumentPreviewCard } from '@/components/internal/DocumentPreviewCard'
import { IconLabel } from '@/components/internal/IconLabel'
import { WeeklyAppointmentsView } from '@/components/internal/WeeklyAppointmentsView'
import { AppointmentsScheduler } from '@/components/internal/AppointmentsScheduler'

export type ComponentSource = 'internal' | 'mui' | 'fullcalendar'

export interface ComponentEntry {
  component: ComponentType<Record<string, unknown>>
  source: ComponentSource
  allowedProps?: string[]
}

export const registry: Record<string, ComponentEntry> = {
  Text: { component: Text as ComponentType<Record<string, unknown>>, source: 'mui' },
  Button: { component: Button as ComponentType<Record<string, unknown>>, source: 'mui' },
  Card: { component: Card as ComponentType<Record<string, unknown>>, source: 'mui' },
  Alert: { component: Alert as ComponentType<Record<string, unknown>>, source: 'mui' },
  Banner: { component: Alert as ComponentType<Record<string, unknown>>, source: 'mui' },
  Row: { component: Row as ComponentType<Record<string, unknown>>, source: 'mui' },
  Column: { component: Column as ComponentType<Record<string, unknown>>, source: 'mui' },
  Spacer: { component: Spacer as ComponentType<Record<string, unknown>>, source: 'mui' },
  Divider: { component: Divider as ComponentType<Record<string, unknown>>, source: 'mui' },
  Select: { component: Select as ComponentType<Record<string, unknown>>, source: 'mui' },
  Dropdown: { component: Select as ComponentType<Record<string, unknown>>, source: 'mui' },
  IconButton: { component: IconButton as ComponentType<Record<string, unknown>>, source: 'mui' },
  SegmentedControl: { component: SegmentedControl as ComponentType<Record<string, unknown>>, source: 'mui' },
  Message: { component: Message as ComponentType<Record<string, unknown>>, source: 'internal' },
  StatusMessage: { component: StatusMessage as ComponentType<Record<string, unknown>>, source: 'internal' },
  FormattedText: { component: FormattedText as ComponentType<Record<string, unknown>>, source: 'internal' },
  Timestamp: { component: Timestamp as ComponentType<Record<string, unknown>>, source: 'internal' },
  GreetingAvatar: { component: GreetingAvatar as ComponentType<Record<string, unknown>>, source: 'internal' },
  DashboardIllustration: { component: DashboardIllustration as ComponentType<Record<string, unknown>>, source: 'internal' },
  FormattedAlert: { component: FormattedAlert as ComponentType<Record<string, unknown>>, source: 'internal' },
  SummaryStat: { component: SummaryStat as ComponentType<Record<string, unknown>>, source: 'internal' },
  WeeklyHeader: { component: WeeklyHeader as ComponentType<Record<string, unknown>>, source: 'internal' },
  AppointmentCard: { component: AppointmentCard as ComponentType<Record<string, unknown>>, source: 'internal' },
  DocumentPreviewCard: { component: DocumentPreviewCard as ComponentType<Record<string, unknown>>, source: 'internal' },
  IconLabel: { component: IconLabel as ComponentType<Record<string, unknown>>, source: 'internal' },
  WeeklyAppointmentsView: { component: WeeklyAppointmentsView as ComponentType<Record<string, unknown>>, source: 'internal' },
  AppointmentsScheduler: { component: AppointmentsScheduler as ComponentType<Record<string, unknown>>, source: 'internal' },
  CalendarScheduler: { component: CalendarScheduler as ComponentType<Record<string, unknown>>, source: 'fullcalendar' },
}

export function getComponent(type: string): ComponentEntry | null {
  return registry[type] ?? null
}

/** Returns all registered component type names (for validation, spec selector, etc.) */
export function getRegisteredTypes(): string[] {
  return Object.keys(registry)
}
