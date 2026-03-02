# SDUI Project Execution Plan

Phased execution plan with user stories. Order is sequential where dependencies exist.

---

## Phase 1: Project Setup

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 1.1 | **Initialize React + TypeScript + Vite** | Create Vite React-TS project with base config | `npm create vite`, TS strict, ESLint |
| 1.2 | **Install dependencies** | Add MUI, FullCalendar, Emotion | package.json with @mui/material, @fullcalendar/*, @emotion/* |
| 1.3 | **Configure folder structure** | Create src/renderer, components, schema, scenarios | Folders per docs/ARCHITECTURE.md |
| 1.4 | **Configure path aliases** | Set up @/ or similar for imports | tsconfig paths, vite resolve |
| 1.5 | **Add MUI ThemeProvider** | Base theme setup in App | Theme wraps app |

---

## Phase 2: Creating Components

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 2.1 | **Register MUI primitives** | Text, Button, Card, Alert, Row, Column, Spacer, Divider | Wrappers map JSON props to MUI |
| 2.2 | **Register Select/Dropdown** | Dropdown, Select from MUI | Options from JSON, action on change |
| 2.3 | **Register IconButton, SegmentedControl** | IconButton, ToggleButtonGroup | Props from JSON |
| 2.4 | **Build Message component** | Chat-style bubble (avatar, timestamp, content) | Internal, registered |
| 2.5 | **Build StatusMessage component** | Success/error with icon | Internal, registered |
| 2.6 | **Build SummaryStat component** | Day's Summary row (label, value, action) | Internal, registered |
| 2.7 | **Build WeeklyHeader component** | Date range + count | Internal, registered |
| 2.8 | **Build AppointmentCard component** | Patient, doctor, insurance, time, status | Internal, registered |
| 2.9 | **Build CalendarScheduler wrapper** | FullCalendar wrapper, config from props | Internal, registered |
| 2.10 | **Create component registry** | Map JSON type → component | registry.ts with all entries |

---

## Phase 3: Demo Environment

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 3.1 | **Create demo JSON fixtures** | Static JSON files for testing | scenarios/*.json |
| 3.2 | **Create demo page route** | /demo or /sdui-demo route | Dev-only or main route |
| 3.3 | **Add role switcher (Doctor/Front Desk)** | Toggle to load different JSON | For scheduler showcase |
| 3.4 | **Add JSON spec selector** | Dropdown or tabs to load different specs | For testing multiple screens |

---

## Phase 4: TypeScript Types for Renderer Schema

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 4.1 | **Define SDUINode type** | type, props, style, action, children | schema/v1.ts |
| 4.2 | **Define Action types** | api, navigate, emit, openForm, openDrawer, openWizard | Union type |
| 4.3 | **Define dataSource / fieldMapping types** | For data binding | schema/v1.ts |
| 4.4 | **Define ComponentEntry type** | For registry | schema/v1.ts |
| 4.5 | **Export schema types** | Public API for renderer | schema/index.ts |

---

## Phase 5: Renderer Tasks

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 5.1 | **Implement parser** | JSON → SDUINode tree | parser.ts, handles nested children |
| 5.2 | **Implement validator** | Validate against schema | Returns errors or valid |
| 5.3 | **Implement renderNode (recursive)** | Lookup registry, render component | engine.tsx |
| 5.4 | **Implement bindActions** | Map action → onClick handler | Action executor stub |
| 5.5 | **Implement action executor** | Handle api, navigate, emit, openForm, openDrawer | action-executor.ts |
| 5.6 | **Implement SDUIRenderer component** | Accept spec prop, parse, render | Main export |
| 5.7 | **Handle unknown component types** | Fallback or skip | No crash on unknown type |
| 5.8 | **Apply style prop** | Pass style to components | sx or style support |

---

## Phase 6: Static View Stories

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 6.1 | **Render simple Text** | Single Text node from JSON | Displays value |
| 6.2 | **Render Button with action** | Button, onClick triggers action | Action executor called |
| 6.3 | **Render Card with children** | Card containing Text, Button | Nested render |
| 6.4 | **Render Row/Column layout** | Row of buttons, Column of cards | Layout correct |
| 6.5 | **Render Alert/Banner** | Alert with message, type | Displays correctly |
| 6.6 | **Render Dropdown** | Select with options from JSON | Options, onChange |
| 6.7 | **Render Message** | Chat bubble from JSON | Avatar, timestamp, content |
| 6.8 | **Render StatusMessage** | Success/error message | Icon + text |
| 6.9 | **Render SummaryStat** | Day's Summary items | Multiple stats in row |

---

## Phase 7: AppShell and Renderer Integration

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 7.1 | **Build AppShell layout** | Header, main content, footer | Per views analysis |
| 7.2 | **Build Header** | Logo, search bar, icons, user profile | Static |
| 7.3 | **Build Footer** | Search/ask bar, nav icons, Day's Summary slot | Static with SummaryStat slot |
| 7.4 | **Integrate SDUIRenderer in main content** | AppShell wraps SDUIRenderer | spec prop drives content |
| 7.5 | **Create screen layout component** | Shell + SDUIRenderer(spec) | Reusable per screen |

---

## Phase 8: API and Data Loading

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 8.1 | **Implement data injector** | Resolve dataSource, fetch, map | data-injector.ts |
| 8.2 | **Support dataSource in parser** | Read dataSource, fieldMapping from nodes | Schema support |
| 8.3 | **Create mock API layer** | Fake endpoints for Phase 1 | /api/appointments, etc. |
| 8.4 | **Inject data into components** | Pass resolved props before render | Components receive data |
| 8.5 | **Handle loading/error states** | Loading spinner, error message | UX for async data |

---

## Phase 9: Doctor and Front Desk Scenarios

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 9.1 | **Create doctor-scheduler.json** | Day view, no overbooking, limited actions | Valid spec |
| 9.2 | **Create front-desk-scheduler.json** | Week view, overbooking, full booking flow | Valid spec |
| 9.3 | **Render Doctor scheduler** | Load doctor spec, render CalendarScheduler | Day view, correct actions |
| 9.4 | **Render Front Desk scheduler** | Load front-desk spec, render CalendarScheduler | Week view, correct actions |
| 9.5 | **Role switcher loads correct spec** | Toggle Doctor/Front Desk → different JSON | Showcase complete |
| 9.6 | **Wire mock appointment data** | dataSource → mock API → inject | Cards show data |

---

## Phase 10: Polish and Demo (Optional)

| # | Story | Description | Acceptance |
|---|-------|-------------|------------|
| 10.1 | **Demo all 6 screens** | JSON specs for screens 1–6 from views | Each renders |
| 10.2 | **Navigation between screens** | Links or router | Flow through referral → scheduler |
| 10.3 | **Error handling** | Invalid JSON, missing component | Graceful fallback |
| 10.4 | **README and run instructions** | How to run, switch roles | Documented |

---

## Dependency Graph (High Level)

```
Phase 1 (Setup) 
    → Phase 2 (Components) 
    → Phase 4 (Types) 
    → Phase 5 (Renderer)
         ↓
Phase 3 (Demo env) ← Phase 5
         ↓
Phase 6 (Static views) — validates renderer
         ↓
Phase 7 (AppShell) — wraps renderer
         ↓
Phase 8 (Data loading) — enables data injection
         ↓
Phase 9 (Doctor + Front Desk) — showcase
         ↓
Phase 10 (Polish)
```

---

## Suggested Sprint Breakdown

| Sprint | Phases | Focus |
|--------|--------|-------|
| **Sprint 1** | 1, 2 (partial) | Setup + MUI components |
| **Sprint 2** | 2 (rest), 4, 5 | Internal components, types, renderer |
| **Sprint 3** | 3, 6, 7 | Demo env, static views, AppShell |
| **Sprint 4** | 8, 9 | Data loading, Doctor + Front Desk |
| **Sprint 5** | 10 | Polish, full demo |
