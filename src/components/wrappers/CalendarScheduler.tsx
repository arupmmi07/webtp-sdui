import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { EventClickArg, EventDropArg } from '@fullcalendar/core'
import type { EventInput } from '@fullcalendar/core'

const VIEW_MAP: Record<string, string> = {
  day: 'timeGridDay',
  week: 'timeGridWeek',
  month: 'dayGridMonth',
  timeGridDay: 'timeGridDay',
  timeGridWeek: 'timeGridWeek',
  dayGridMonth: 'dayGridMonth',
  dayGridWeek: 'dayGridWeek',
}

function parseSlotDuration(input: string | number | undefined): string | undefined {
  if (input == null) return undefined
  if (typeof input === 'number') return `${input}:00:00`
  const s = String(input).trim()
  if (!s) return undefined
  if (/^\d+$/.test(s)) return `${s}:00:00`
  if (/^\d+m$/.test(s)) return `00:${s.slice(0, -1).padStart(2, '0')}:00`
  if (/^\d+h$/.test(s)) return `${s.slice(0, -1).padStart(2, '0')}:00:00`
  if (/^\d+:\d+:\d+$/.test(s) || /^\d+:\d+$/.test(s)) return s
  return s
}

function parseBusinessHours(workingHours?: { start?: string; end?: string }): object | undefined {
  if (!workingHours?.start || !workingHours?.end) return undefined
  return {
    daysOfWeek: [1, 2, 3, 4, 5],
    startTime: workingHours.start,
    endTime: workingHours.end,
  }
}

interface CalendarSchedulerProps {
  view?: string
  slotDuration?: string | number
  workingHours?: { start?: string; end?: string }
  allowOverbooking?: boolean
  groupBy?: string
  events?: EventInput[]
  onSlotClick?: (date: Date, allDay: boolean) => void
  onEventClick?: (eventId: string, event: EventClickArg) => void
  onEventDrop?: (eventId: string, dropArg: EventDropArg) => void
  [key: string]: unknown
}

export function CalendarScheduler({
  view = 'timeGridWeek',
  slotDuration,
  workingHours,
  allowOverbooking = false,
  events = [],
  onSlotClick,
  onEventClick,
  onEventDrop,
  ...rest
}: CalendarSchedulerProps) {
  const initialView = VIEW_MAP[view] ?? view
  const slotDurationStr = parseSlotDuration(slotDuration as string | number)
  const businessHours = parseBusinessHours(workingHours as { start?: string; end?: string })

  return (
    <FullCalendar
      plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
      initialView={initialView}
      slotDuration={slotDurationStr}
      businessHours={businessHours}
  editable
  eventOverlap={allowOverbooking}
      events={events as EventInput[]}
      dateClick={(arg) => onSlotClick?.(arg.date, arg.allDay)}
      eventClick={(arg) => onEventClick?.(arg.event.id ?? '', arg)}
      eventDrop={(arg) => onEventDrop?.(arg.event.id ?? '', arg)}
      headerToolbar={{
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay',
      }}
      {...rest}
    />
  )
}
