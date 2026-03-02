# SDUI JSON Schema v1

## Node Structure

Every node in the tree has:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Registry key (e.g., "Text", "Button", "CalendarScheduler") |
| `props` | object | No | Passed to component |
| `style` | object | No | Applied by renderer (padding, margin, etc.) |
| `action` | Action | No | Bound to primary interaction (e.g., onClick) |
| `children` | Node[] | No | Child nodes |

## Example: Card with Button

```json
{
  "type": "Card",
  "style": { "padding": 16 },
  "children": [
    {
      "type": "Text",
      "props": { "value": "Order Summary", "variant": "h6" }
    },
    {
      "type": "Button",
      "props": { "label": "Pay Now", "variant": "primary" },
      "action": {
        "type": "api",
        "endpoint": "/api/pay"
      }
    }
  ]
}
```

## Action Types

```typescript
type Action =
  | { type: "api"; endpoint: string }
  | { type: "navigate"; to: string }
  | { type: "emit"; event: string }
  | { type: "openForm"; form: string }
  | { type: "openDrawer"; panel: string }
  | { type: "openWizard"; flow: string };
```

## Layout Components

- **Row**: Horizontal layout, children in a row
- **Column**: Vertical layout, children in a column
- **Grid**: Grid layout (props: columns, gap)
- **Spacer**: Flexible space

## EMR Scheduler Example

```json
{
  "type": "CalendarScheduler",
  "props": {
    "view": "day",
    "slotDuration": "15m",
    "workingHours": { "start": "09:00", "end": "17:00" },
    "allowOverbooking": false
  },
  "actions": {
    "onSlotClick": { "type": "openForm", "form": "NewAppointment" },
    "onEventClick": { "type": "openDrawer", "panel": "AppointmentDetails" }
  }
}
```

## Data Binding (Not Data)

JSON defines **where** data comes from, not the data itself:

```json
{
  "type": "List",
  "props": {
    "dataSource": "/api/appointments",
    "fieldMapping": { "title": "patientName", "start": "slotStart" }
  }
}
```

- `dataSource` — API path, context key, or binding ID
- `fieldMapping` — how fetched data maps to component props
- **Actual data** — fetched by browser at runtime, injected by renderer

## Reserved / Disallowed

- No `eval`, no arbitrary JS
- No npm package references in JSON
- No PHI or sensitive data in spec
- **No inline data payloads** — use dataSource + injection instead
