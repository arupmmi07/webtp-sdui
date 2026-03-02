# Component Strategy: Internal vs External + Library Choice

Components are either **internal** (we build) or **external** (from a lib). All are registered in the component registry so the renderer can resolve JSON `type` → component and build the UI.

---

## 1. Library Recommendations

### Primary: MUI (Material UI)

| Factor | Notes |
|--------|-------|
| **Components** | Button, Card, Alert, Typography, Select, IconButton, ToggleButtonGroup, Stack, Box |
| **Fit** | Enterprise, healthcare dashboards, comprehensive |
| **Bundle** | ~88–200KB gzipped (tree-shakeable) |
| **Theming** | ThemeProvider, design tokens |
| **Docs** | Strong, widely used |

**Covers**: Text, Button, Card, Alert/Banner, Dropdown (Select), IconButton, Row/Column (Stack/Box), SegmentedControl (ToggleButtonGroup)

### Secondary: FullCalendar

| Factor | Notes |
|--------|-------|
| **Purpose** | CalendarScheduler — day/week views, slots, events |
| **Package** | `@fullcalendar/react`, `@fullcalendar/core`, `@fullcalendar/daygrid`, `@fullcalendar/timegrid` |
| **Fit** | Standard for appointment scheduling |

**Covers**: CalendarScheduler (we wrap FullCalendar)

### Alternative Considered: Ant Design

- Strong for enterprise dashboards
- Larger bundle (~120–300KB)
- MUI chosen for broader ecosystem and familiarity

---

## 2. Component Registry Mapping

| JSON `type` | Source | Implementation |
|-------------|--------|----------------|
| **Text** | MUI | `Typography` |
| **Button** | MUI | `Button` |
| **Card** | MUI | `Card`, `CardContent` |
| **Alert** | MUI | `Alert` |
| **Banner** | MUI | `Alert` (variant) |
| **Dropdown** | MUI | `Select` + `MenuItem` |
| **Select** | MUI | `Select` |
| **IconButton** | MUI | `IconButton` |
| **Row** | MUI | `Stack` (direction="row") |
| **Column** | MUI | `Stack` (direction="column") |
| **Spacer** | MUI | `Box` (flex: 1) |
| **Divider** | MUI | `Divider` |
| **SegmentedControl** | MUI | `ToggleButtonGroup` |
| **Image** | Internal | `img` or MUI `Box` with background |
| **Message** | Internal | Card + custom layout (avatar, timestamp, content) |
| **StatusMessage** | Internal | Alert variant with icon + color |
| **SummaryStat** | Internal | Row of Text/Badge items |
| **WeeklyHeader** | Internal | Custom (date range + count) |
| **AppointmentCard** | Internal | Custom card (patient, doctor, status) |
| **CalendarScheduler** | Internal | Wrapper around FullCalendar |

---

## 3. Internal vs External Summary

### External (from MUI)

- Text, Button, Card, Alert, Banner, Dropdown, Select, IconButton
- Row, Column, Spacer, Divider
- SegmentedControl

### External (FullCalendar)

- Used inside CalendarScheduler wrapper only

### Internal (we build)

- **Message** — Chat-style bubble (Card + avatar + timestamp + content)
- **StatusMessage** — Success/error with icon (Alert variant)
- **SummaryStat** — Day's Summary row (label + value + optional action)
- **WeeklyHeader** — "26 Feb - 01 Mar 2026 (7)"
- **AppointmentCard** — Patient, doctor, insurance, time, status indicators
- **CalendarScheduler** — Wrapper that configures FullCalendar from JSON props

---

## 4. Registry Entry Shape

```typescript
type ComponentSource = "internal" | "mui" | "fullcalendar";

type ComponentEntry = {
  component: React.ComponentType<any>;
  source: ComponentSource;
  allowedProps?: string[];  // optional allowlist
};

const registry: Record<string, ComponentEntry> = {
  Text: { component: MuiTypography, source: "mui" },
  Button: { component: MuiButton, source: "mui" },
  Card: { component: MuiCard, source: "mui" },
  Alert: { component: MuiAlert, source: "mui" },
  // ...
  Message: { component: Message, source: "internal" },
  AppointmentCard: { component: AppointmentCard, source: "internal" },
  CalendarScheduler: { component: CalendarSchedulerWrapper, source: "internal" },
};
```

---

## 5. Dependencies for Project Setup

```json
{
  "dependencies": {
    "@emotion/react": "^11.x",
    "@emotion/styled": "^11.x",
    "@fullcalendar/core": "^6.x",
    "@fullcalendar/daygrid": "^6.x",
    "@fullcalendar/react": "^6.x",
    "@fullcalendar/timegrid": "^6.x",
    "@mui/icons-material": "^5.x",
    "@mui/material": "^5.x",
    "react": "^18.x",
    "react-dom": "^18.x"
  },
  "devDependencies": {
    "@types/react": "^18.x",
    "typescript": "^5.x",
    "vite": "^5.x"
  }
}
```

---

## 6. Wrapper Components

Some MUI components need thin wrappers to match our JSON props:

| Component | Wrapper | Reason |
|-----------|---------|--------|
| Typography | Text | Map `value` → `children`, `variant` |
| Alert | Banner | Alias; same component |
| Stack | Row/Column | Map `direction` from type name |

These wrappers live in `components/internal/` or `components/wrappers/` and are registered under the JSON type name.
