# SDUI Runtime Renderer — Functional Acceptance Criteria (FA)

> **Owner:** SDUI Project Lead  
> **Workstream:** SDUI POC  
> **Lifecycle:** Active — Phase 1 POC through Doctor + Front Desk showcase

---

## Business Goal

Achieve a **Runtime UI Composition Engine** that:

- Renders UI from JSON specs at runtime (no app redeploy for UI changes)
- Supports Doctor vs Front Desk scheduler scenarios from different JSON (showcase)
- Coexists with static React UI (AppShell + SDUI content area)
- Uses client-side data binding (JSON = structure + dataSource; browser fetches and injects)

---

## Scope (In)

| Story ID    | Title                                                       |
| ----------- | ----------------------------------------------------------- |
| SDUI-P1-01  | Initialize React + TypeScript + Vite                         |
| SDUI-P1-02  | Install dependencies (MUI, FullCalendar, Emotion)            |
| SDUI-P1-03  | Configure folder structure                                  |
| SDUI-P1-04  | Configure path aliases                                      |
| SDUI-P1-05  | Add MUI ThemeProvider                                       |
| SDUI-P2-01  | Register MUI primitives (Text, Button, Card, Alert, etc.)    |
| SDUI-P2-02  | Register Select/Dropdown                                    |
| SDUI-P2-03  | Register IconButton, SegmentedControl                        |
| SDUI-P2-04  | Build Message component                                     |
| SDUI-P2-05  | Build StatusMessage component                                |
| SDUI-P2-06  | Build SummaryStat component                                 |
| SDUI-P2-07  | Build WeeklyHeader component                                |
| SDUI-P2-08  | Build AppointmentCard component                             |
| SDUI-P2-09  | Build CalendarScheduler wrapper                              |
| SDUI-P2-10  | Create component registry                                    |
| SDUI-P3-01  | Create demo JSON fixtures                                   |
| SDUI-P3-02  | Create demo page route                                      |
| SDUI-P3-03  | Add role switcher (Doctor/Front Desk)                        |
| SDUI-P3-04  | Add JSON spec selector                                      |
| SDUI-P4-01  | Define SDUINode type                                        |
| SDUI-P4-02  | Define Action types                                         |
| SDUI-P4-03  | Define dataSource / fieldMapping types                       |
| SDUI-P4-04  | Define ComponentEntry type                                   |
| SDUI-P4-05  | Export schema types                                         |
| SDUI-P5-01  | Implement parser                                            |
| SDUI-P5-02  | Implement validator                                         |
| SDUI-P5-03  | Implement renderNode (recursive)                            |
| SDUI-P5-04  | Implement bindActions                                       |
| SDUI-P5-05  | Implement action executor                                    |
| SDUI-P5-06  | Implement SDUIRenderer component                             |
| SDUI-P5-07  | Handle unknown component types                              |
| SDUI-P5-08  | Apply style prop                                            |
| SDUI-P6-01  | Render simple Text                                          |
| SDUI-P6-02  | Render Button with action                                    |
| SDUI-P6-03  | Render Card with children                                   |
| SDUI-P6-04  | Render Row/Column layout                                    |
| SDUI-P6-05  | Render Alert/Banner                                         |
| SDUI-P6-06  | Render Dropdown                                             |
| SDUI-P6-07  | Render Message                                              |
| SDUI-P6-08  | Render StatusMessage                                        |
| SDUI-P6-09  | Render SummaryStat                                          |
| SDUI-P7-01  | Build AppShell layout                                       |
| SDUI-P7-02  | Build Header                                                |
| SDUI-P7-03  | Build Footer                                                |
| SDUI-P7-04  | Integrate SDUIRenderer in main content                       |
| SDUI-P7-05  | Create screen layout component                               |
| SDUI-P8-01  | Implement data injector                                     |
| SDUI-P8-02  | Support dataSource in parser                                 |
| SDUI-P8-03  | Create mock API layer                                       |
| SDUI-P8-04  | Inject data into components                                  |
| SDUI-P8-05  | Handle loading/error states                                  |
| SDUI-P9-01  | Create doctor-scheduler.json                                 |
| SDUI-P9-02  | Create front-desk-scheduler.json                            |
| SDUI-P9-03  | Render Doctor scheduler                                     |
| SDUI-P9-04  | Render Front Desk scheduler                                 |
| SDUI-P9-05  | Role switcher loads correct spec                             |
| SDUI-P9-06  | Wire mock appointment data                                   |
| SDUI-P10-01 | Demo all 6 screens                                          |
| SDUI-P10-02 | Navigation between screens                                  |
| SDUI-P10-03 | Error handling                                              |
| SDUI-P10-04 | README and run instructions                                 |

---

## Scope (Out)

- Visual drag-and-drop builder
- Cross-platform renderer (Web first only)
- Server-side data in JSON (PHI constraint; client fetches)
- GraphQL backend (Phase 2)
- Conditional visibility / feature flags (Phase 2)

---

## Phase 1: Project Setup

### SDUI-P1-01 — Initialize React + TypeScript + Vite

#### Problem Statement

The project needs a modern React + TypeScript foundation with fast dev feedback. Vite provides HMR and minimal config.

#### Functional Acceptance Criteria

- [ ] Project created via `npm create vite@latest` (or equivalent) with React + TypeScript template.
- [ ] TypeScript strict mode enabled in `tsconfig.json`.
- [ ] ESLint configured for React + TypeScript.
- [ ] App runs with `npm run dev` and displays a minimal placeholder.

---

### SDUI-P1-02 — Install dependencies (MUI, FullCalendar, Emotion)

#### Problem Statement

The renderer requires MUI for base components and FullCalendar for the scheduler. Emotion is a peer of MUI.

#### Functional Acceptance Criteria

- [ ] `@mui/material`, `@mui/icons-material`, `@emotion/react`, `@emotion/styled` installed.
- [ ] `@fullcalendar/react`, `@fullcalendar/core`, `@fullcalendar/daygrid`, `@fullcalendar/timegrid` installed.
- [ ] `package.json` reflects all dependencies with compatible versions.
- [ ] No peer dependency warnings on `npm install`.

---

### SDUI-P1-03 — Configure folder structure

#### Problem Statement

The architecture requires clear separation of renderer, components, schema, and scenarios.

#### Functional Acceptance Criteria

- [ ] `src/renderer/` exists for engine, parser, validator, registry, action-executor.
- [ ] `src/components/internal/` and `src/components/wrappers/` exist.
- [ ] `src/schema/` exists for types.
- [ ] `src/scenarios/scheduler/` exists for JSON specs.
- [ ] Structure matches `docs/ARCHITECTURE.md`.

---

### SDUI-P1-04 — Configure path aliases

#### Problem Statement

Deep imports like `../../../components/` are error-prone. Path aliases improve readability.

#### Functional Acceptance Criteria

- [ ] `tsconfig.json` includes `paths` (e.g. `@/*` → `src/*`).
- [ ] Vite `resolve.alias` matches tsconfig paths.
- [ ] Imports like `@/renderer/engine` resolve correctly.

---

### SDUI-P1-05 — Add MUI ThemeProvider

#### Problem Statement

MUI components require a theme context. The app must wrap content in ThemeProvider.

#### Functional Acceptance Criteria

- [ ] `ThemeProvider` wraps the root app (or main content).
- [ ] A base theme is applied (light mode minimum).
- [ ] MUI components render with consistent styling.

---

## Phase 2: Creating Components

### SDUI-P2-01 — Register MUI primitives (Text, Button, Card, Alert, Row, Column, Spacer, Divider)

#### Problem Statement

The renderer must map JSON `type` to React components. MUI provides Text (Typography), Button, Card, Alert, Stack (Row/Column), Box (Spacer), Divider.

#### Functional Acceptance Criteria

- [ ] Each primitive has a thin wrapper (if needed) that maps JSON props to MUI props.
- [ ] `Text` maps `value` → children, `variant` → Typography variant.
- [ ] `Row` and `Column` map to `Stack` with `direction="row"` and `direction="column"`.
- [ ] All primitives are registered in the component registry under their JSON type name.

---

### SDUI-P2-02 — Register Select/Dropdown

#### Problem Statement

Screens 2–4 require dropdowns (e.g. "Request Revised Form" options). MUI Select provides this.

#### Functional Acceptance Criteria

- [ ] `Dropdown` and `Select` are registered (can be same component or alias).
- [ ] Options are provided via JSON (e.g. `options: [{ value, label }]`).
- [ ] `onChange` triggers the action executor when an option is selected.
- [ ] Selected value is controllable from props.

---

### SDUI-P2-03 — Register IconButton, SegmentedControl

#### Problem Statement

Message action icons (mail, chat, document) and view toggle (Weekly/Daily) require IconButton and ToggleButtonGroup.

#### Functional Acceptance Criteria

- [ ] `IconButton` accepts `icon` (name or component) and `action` from JSON.
- [ ] `SegmentedControl` maps to MUI `ToggleButtonGroup` with options from JSON.
- [ ] Active state and `onChange` are driven by JSON/config.

---

### SDUI-P2-04 — Build Message component

#### Problem Statement

Screens 2–5 show chat-style message bubbles (avatar, timestamp, content, action icons).

#### Functional Acceptance Criteria

- [ ] `Message` renders a card-like bubble with avatar (left), timestamp, and content.
- [ ] Content supports multi-line text from JSON.
- [ ] Optional action icons (mail, chat, document) render below content.
- [ ] Component is internal (we build it) and registered under type `Message`.

---

### SDUI-P2-05 — Build StatusMessage component

#### Problem Statement

Screens 4–5 show success/error status messages with icon (e.g. "Email successfully sent").

#### Functional Acceptance Criteria

- [ ] `StatusMessage` displays icon + text with configurable severity (success, error, warning).
- [ ] Severity drives color (e.g. green for success, red for error).
- [ ] Component is internal and registered under type `StatusMessage`.

---

### SDUI-P2-06 — Build SummaryStat component

#### Problem Statement

Day's Summary bar (e.g. "28 Due appointments | 3 missing authorization") appears on all screens.

#### Functional Acceptance Criteria

- [ ] `SummaryStat` renders a row of items, each with label and value.
- [ ] Items are provided via JSON (e.g. `items: [{ label, value, action? }]`).
- [ ] Optional "+8 More" or similar action is supported.
- [ ] Component is internal and registered under type `SummaryStat`.

---

### SDUI-P2-07 — Build WeeklyHeader component

#### Problem Statement

Scheduler screen 6 shows weekly grouping headers (e.g. "26 Feb - 01 Mar 2026 (7)").

#### Functional Acceptance Criteria

- [ ] `WeeklyHeader` displays date range and count.
- [ ] Props: `dateRange` (string or formatted), `count` (number).
- [ ] Component is internal and registered under type `WeeklyHeader`.

---

### SDUI-P2-08 — Build AppointmentCard component

#### Problem Statement

Scheduler displays appointment cards with patient, doctor, insurance, time, and status (Valid, Expiring, Invalid, High No-Show).

#### Functional Acceptance Criteria

- [ ] `AppointmentCard` displays: patient name, doctor name, insurance, date/time, status indicator.
- [ ] Status drives visual styling (green/orange/red, badge).
- [ ] Optional `action` for click (e.g. openDrawer).
- [ ] Component is internal and registered under type `AppointmentCard`.

---

### SDUI-P2-09 — Build CalendarScheduler wrapper

#### Problem Statement

FullCalendar must be wrapped so JSON config (view, slotDuration, actions) drives behavior.

#### Functional Acceptance Criteria

- [ ] `CalendarScheduler` wraps FullCalendar.
- [ ] Props from JSON: `view` (day/week), `slotDuration`, `workingHours`, `allowOverbooking`, `groupBy` (optional).
- [ ] Actions: `onSlotClick`, `onEventClick` (and optionally `onEventDrag`) are bound via action executor.
- [ ] Component is internal and registered under type `CalendarScheduler`.

---

### SDUI-P2-10 — Create component registry

#### Problem Statement

The renderer needs a single registry mapping JSON `type` → React component.

#### Functional Acceptance Criteria

- [ ] `registry.ts` (or equivalent) exports a `Record<string, ComponentEntry>`.
- [ ] Every component from P2-01 through P2-09 is registered.
- [ ] `ComponentEntry` includes `component`, `source` (internal | mui | fullcalendar).
- [ ] Lookup by `node.type` returns the correct component or null for unknown types.

---

## Phase 3: Demo Environment

### SDUI-P3-01 — Create demo JSON fixtures

#### Problem Statement

Phase 1 uses static JSON. We need fixture files to test the renderer.

#### Functional Acceptance Criteria

- [ ] `src/scenarios/scheduler/doctor-scheduler.json` exists (placeholder or minimal valid spec).
- [ ] `src/scenarios/scheduler/front-desk-scheduler.json` exists.
- [ ] Additional fixtures for static view tests (e.g. simple Card, Button) exist.
- [ ] All fixtures are valid against schema v1.

---

### SDUI-P3-02 — Create demo page route

#### Problem Statement

Developers need a way to view the SDUI renderer output.

#### Functional Acceptance Criteria

- [ ] A route exists (e.g. `/demo` or `/sdui-demo`) that renders `SDUIRenderer` with a spec.
- [ ] Route is reachable from the app (dev or main navigation).
- [ ] Default spec loads on page load.

---

### SDUI-P3-03 — Add role switcher (Doctor/Front Desk)

#### Problem Statement

The showcase requires switching between Doctor and Front Desk scheduler specs.

#### Functional Acceptance Criteria

- [ ] A control (toggle, dropdown, or tabs) allows selecting "Doctor" or "Front Desk".
- [ ] Selecting Doctor loads `doctor-scheduler.json` and passes it to `SDUIRenderer`.
- [ ] Selecting Front Desk loads `front-desk-scheduler.json` and passes it to `SDUIRenderer`.
- [ ] UI updates when role changes (no full page reload required).

---

### SDUI-P3-04 — Add JSON spec selector

#### Problem Statement

Testing multiple screens requires loading different JSON specs.

#### Functional Acceptance Criteria

- [ ] A control (dropdown or tabs) lists available JSON specs.
- [ ] Selecting a spec loads it and passes it to `SDUIRenderer`.
- [ ] At least: Doctor scheduler, Front Desk scheduler, and 1–2 static view specs are available.

---

## Phase 4: TypeScript Types for Renderer Schema

### SDUI-P4-01 — Define SDUINode type

#### Problem Statement

The parser produces a typed tree. We need a canonical `SDUINode` type.

#### Functional Acceptance Criteria

- [ ] `SDUINode` has: `type: string`, `props?: Record<string, unknown>`, `style?: Record<string, unknown>`, `action?: Action`, `children?: SDUINode[]`.
- [ ] Type is exported from `src/schema/` and used by parser and renderer.

---

### SDUI-P4-02 — Define Action types

#### Problem Statement

Actions are abstract (api, navigate, emit, openForm, openDrawer, openWizard). We need a union type.

#### Functional Acceptance Criteria

- [ ] `Action` is a discriminated union covering: `api`, `navigate`, `emit`, `openForm`, `openDrawer`, `openWizard`.
- [ ] Each variant has the required payload (e.g. `api` has `endpoint`).
- [ ] Type is exported and used by action executor.

---

### SDUI-P4-03 — Define dataSource / fieldMapping types

#### Problem Statement

Data binding uses `dataSource` and `fieldMapping` in node props. Types must support this.

#### Functional Acceptance Criteria

- [ ] `dataSource` is typed (string for API path or context key).
- [ ] `fieldMapping` is typed as `Record<string, string>` (fetched field → component prop).
- [ ] Types are part of schema and documented in `docs/SCHEMA-V1.md`.

---

### SDUI-P4-04 — Define ComponentEntry type

#### Problem Statement

The registry needs a typed entry structure.

#### Functional Acceptance Criteria

- [ ] `ComponentEntry` has: `component: React.ComponentType<any>`, `source: 'internal' | 'mui' | 'fullcalendar'`, `allowedProps?: string[]` (optional).
- [ ] Type is exported and used by registry.

---

### SDUI-P4-05 — Export schema types

#### Problem Statement

Parser, validator, and renderer need a single import surface.

#### Functional Acceptance Criteria

- [ ] `src/schema/index.ts` (or `v1.ts`) exports: `SDUINode`, `Action`, `ComponentEntry`, and data binding types.
- [ ] No circular dependencies.
- [ ] Types are usable from `@/schema` (or configured alias).

---

## Phase 5: Renderer Tasks

### SDUI-P5-01 — Implement parser

#### Problem Statement

Raw JSON must be parsed into an `SDUINode` tree.

#### Functional Acceptance Criteria

- [ ] `parse(spec: unknown): SDUINode | SDUINode[]` converts JSON to typed tree.
- [ ] Nested `children` are parsed recursively.
- [ ] Invalid input returns a parse error or throws with a clear message (no silent failure).

---

### SDUI-P5-02 — Implement validator

#### Problem Statement

Parsed nodes should be validated before rendering.

#### Functional Acceptance Criteria

- [ ] `validate(nodes: SDUINode[]): { valid: boolean; errors?: string[] }` checks structure.
- [ ] Unknown `type` values are reported (or allowed with fallback per P5-07).
- [ ] Required fields (e.g. `type`) are validated.

---

### SDUI-P5-03 — Implement renderNode (recursive)

#### Problem Statement

The core render loop looks up components and renders them recursively.

#### Functional Acceptance Criteria

- [ ] `renderNode(node: SDUINode): ReactNode` looks up `node.type` in registry.
- [ ] Renders the component with `node.props` (and resolved data when injector is wired).
- [ ] Recursively renders `node.children` as children of the component.
- [ ] Returns `null` or fallback for unknown types (per P5-07).

---

### SDUI-P5-04 — Implement bindActions

#### Problem Statement

JSON `action` must be bound to component event handlers (e.g. onClick).

#### Functional Acceptance Criteria

- [ ] `bindActions(props, action): props` merges an `onClick` (or appropriate handler) that calls `actionExecutor.execute(action)`.
- [ ] When `action` is absent, no handler is added.
- [ ] Handler is correctly bound so `this` and closure work in React.

---

### SDUI-P5-05 — Implement action executor

#### Problem Statement

Actions (api, navigate, emit, openForm, openDrawer, openWizard) must be executed.

#### Functional Acceptance Criteria

- [ ] `execute(action: Action)` handles each action type.
- [ ] `api`: calls fetch (or injected API client) with `endpoint`.
- [ ] `navigate`: calls router (or window.location) with `to`.
- [ ] `emit`: dispatches custom event.
- [ ] `openForm`, `openDrawer`, `openWizard`: invoke app-level handlers (can be stubs in Phase 1).
- [ ] Executor is injectable or configurable for testing.

---

### SDUI-P5-06 — Implement SDUIRenderer component

#### Problem Statement

The main export is a React component that accepts a spec and renders the UI.

#### Functional Acceptance Criteria

- [ ] `<SDUIRenderer spec={spec} />` accepts `spec` as object or JSON string.
- [ ] Component parses, validates (or logs errors), and renders the root node(s).
- [ ] Renders nothing or error UI when spec is invalid.
- [ ] Component is the primary export of the renderer package/module.

---

### SDUI-P5-07 — Handle unknown component types

#### Problem Statement

JSON may reference components not yet registered. The app must not crash.

#### Functional Acceptance Criteria

- [ ] When `node.type` is not in registry, renderer skips the node or renders a fallback (e.g. placeholder div with type name).
- [ ] No uncaught exception.
- [ ] Optional: log warning in development.

---

### SDUI-P5-08 — Apply style prop

#### Problem Statement

JSON nodes can include `style` for layout and appearance.

#### Functional Acceptance Criteria

- [ ] `node.style` is applied to the component (via `sx`, `style`, or wrapper).
- [ ] Style values (e.g. padding, margin, fontSize) are passed through correctly.
- [ ] MUI `sx` prop is preferred where applicable.

---

## Phase 6: Static View Stories

### SDUI-P6-01 through SDUI-P6-09 — Render each component from JSON

#### Problem Statement

Each SDUI component must be verifiable via a JSON spec. These stories validate the renderer end-to-end.

#### Functional Acceptance Criteria (per component)

- [ ] **Text (P6-01)**: JSON with `{ type: "Text", props: { value: "Hello" } }` displays "Hello".
- [ ] **Button (P6-02)**: Button with `action` triggers action executor on click.
- [ ] **Card (P6-03)**: Card with children renders nested content.
- [ ] **Row/Column (P6-04)**: Row of buttons, Column of cards render with correct layout.
- [ ] **Alert/Banner (P6-05)**: Alert with message and type displays correctly.
- [ ] **Dropdown (P6-06)**: Select with options from JSON; onChange works.
- [ ] **Message (P6-07)**: Chat bubble with avatar, timestamp, content renders.
- [ ] **StatusMessage (P6-08)**: Success/error message with icon renders.
- [ ] **SummaryStat (P6-09)**: Multiple stats in a row render.

---

## Phase 7: AppShell and Renderer Integration

### SDUI-P7-01 — Build AppShell layout

#### Problem Statement

The app needs a shell (header, main, footer) per the views analysis. Main content hosts SDUI.

#### Functional Acceptance Criteria

- [ ] AppShell has three regions: header (top), main (center), footer (bottom).
- [ ] Main region is scrollable and hosts `SDUIRenderer`.
- [ ] Layout is responsive (minimum: desktop; mobile can be Phase 2).

---

### SDUI-P7-02 — Build Header

#### Problem Statement

Header includes logo, search bar, icons, user profile. Static per views analysis.

#### Functional Acceptance Criteria

- [ ] Logo (webpt or placeholder) on the left.
- [ ] Search bar (placeholder) in center.
- [ ] Icons (grid, notifications, chat) and user profile on the right.
- [ ] Header is static (not SDUI-driven).

---

### SDUI-P7-03 — Build Footer

#### Problem Statement

Footer has search/ask bar, nav icons (History, Tasks, Activities), and Day's Summary slot.

#### Functional Acceptance Criteria

- [ ] Search/ask input at bottom center.
- [ ] Nav icons with labels (History, 12 Tasks, 5 Activities — counts can be static for now).
- [ ] Day's Summary slot can host `SummaryStat` (SDUI) or static placeholder.
- [ ] Footer is static structure; Summary content can be SDUI.

---

### SDUI-P7-04 — Integrate SDUIRenderer in main content

#### Problem Statement

AppShell must wrap SDUIRenderer so spec drives main content.

#### Functional Acceptance Criteria

- [ ] Main content area renders `<SDUIRenderer spec={spec} />`.
- [ ] `spec` is provided by route, role switcher, or spec selector.
- [ ] Shell (header + footer) remains visible while content updates.

---

### SDUI-P7-05 — Create screen layout component

#### Problem Statement

A reusable pattern: Shell + SDUIRenderer(spec) per screen.

#### Functional Acceptance Criteria

- [ ] A `ScreenLayout` (or equivalent) component accepts `spec` and renders AppShell + SDUIRenderer.
- [ ] Component is reusable across demo routes.
- [ ] Optional: `title` or `breadcrumb` prop for screen context.

---

## Phase 8: API and Data Loading

### SDUI-P8-01 — Implement data injector

#### Problem Statement

Nodes with `dataSource` need data fetched and injected before render.

#### Functional Acceptance Criteria

- [ ] `data-injector.ts` (or equivalent) resolves `dataSource` and fetches data.
- [ ] `fieldMapping` is applied to map fetched fields to component props.
- [ ] Resolved data is passed to components by the renderer.
- [ ] Injector is async-aware (renderer handles loading state).

---

### SDUI-P8-02 — Support dataSource in parser

#### Problem Statement

Parser and schema must recognize `dataSource` and `fieldMapping` in nodes.

#### Functional Acceptance Criteria

- [ ] Parser preserves `dataSource` and `fieldMapping` in node props.
- [ ] Schema types include these fields.
- [ ] Renderer invokes data injector for nodes with `dataSource`.

---

### SDUI-P8-03 — Create mock API layer

#### Problem Statement

Phase 1 has no backend. Mock endpoints simulate appointments, summaries, etc.

#### Functional Acceptance Criteria

- [ ] Mock endpoints exist (e.g. `/api/appointments`, `/api/day-summary`).
- [ ] Endpoints return JSON compatible with `fieldMapping`.
- [ ] Can use MSW, static JSON, or simple Express/Vite proxy.
- [ ] Mock is clearly separated from real API (easy to swap in Phase 2).

---

### SDUI-P8-04 — Inject data into components

#### Problem Statement

Components must receive resolved data as props.

#### Functional Acceptance Criteria

- [ ] For nodes with `dataSource`, renderer fetches, maps, and passes resolved props.
- [ ] Components receive data in the shape expected (e.g. `patient`, `doctor` for AppointmentCard).
- [ ] List-like components (e.g. appointment cards) receive array data and render multiple instances.

---

### SDUI-P8-05 — Handle loading/error states

#### Problem Statement

Async data fetch can be loading or fail. UX must reflect this.

#### Functional Acceptance Criteria

- [ ] Loading state: show spinner or skeleton while data is fetching.
- [ ] Error state: show error message when fetch fails.
- [ ] Retry or dismiss action is available (optional).
- [ ] No uncaught promise rejections.

---

## Phase 9: Doctor and Front Desk Scenarios

### SDUI-P9-01 — Create doctor-scheduler.json

#### Problem Statement

Doctor view spec: day view, no overbooking, limited actions.

#### Functional Acceptance Criteria

- [ ] JSON is valid against schema v1.
- [ ] Contains `CalendarScheduler` with: `view: "day"`, `slotDuration`, `allowOverbooking: false`.
- [ ] Actions: `onSlotClick` (openForm), `onEventClick` (openDrawer).
- [ ] No bulk or booking-wizard actions.

---

### SDUI-P9-02 — Create front-desk-scheduler.json

#### Problem Statement

Front Desk view spec: week view, overbooking, full booking flow.

#### Functional Acceptance Criteria

- [ ] JSON is valid against schema v1.
- [ ] Contains `CalendarScheduler` with: `view: "week"`, `groupBy: "doctor"`, `allowOverbooking: true`.
- [ ] Actions: `onSlotClick` (openWizard), `onEventDrag` (rescheduleWithConfirmation).
- [ ] Includes `dataSource` for appointments (or equivalent for data injection).

---

### SDUI-P9-03 — Render Doctor scheduler

#### Problem Statement

Loading doctor spec must render the scheduler in Doctor mode.

#### Functional Acceptance Criteria

- [ ] Loading `doctor-scheduler.json` renders CalendarScheduler in day view.
- [ ] Slot click triggers openForm action (or stub).
- [ ] Event click triggers openDrawer action (or stub).
- [ ] No overbooking UI/behavior.

---

### SDUI-P9-04 — Render Front Desk scheduler

#### Problem Statement

Loading front-desk spec must render the scheduler in Front Desk mode.

#### Functional Acceptance Criteria

- [ ] Loading `front-desk-scheduler.json` renders CalendarScheduler in week view.
- [ ] Grouping by doctor is visible (if supported by FullCalendar config).
- [ ] Slot click triggers openWizard action (or stub).
- [ ] Overbooking is allowed (config passed to wrapper).

---

### SDUI-P9-05 — Role switcher loads correct spec

#### Problem Statement

The showcase requires toggling Doctor/Front Desk and seeing different UI.

#### Functional Acceptance Criteria

- [ ] Selecting "Doctor" loads and renders `doctor-scheduler.json`.
- [ ] Selecting "Front Desk" loads and renders `front-desk-scheduler.json`.
- [ ] Switching roles updates the scheduler without full reload.
- [ ] The difference (day vs week, actions) is clearly visible.

---

### SDUI-P9-06 — Wire mock appointment data

#### Problem Statement

Scheduler should display appointment cards with real-looking data from mock API.

#### Functional Acceptance Criteria

- [ ] `dataSource` in scheduler/appointment nodes points to mock API.
- [ ] Mock API returns appointment-like data (patient, doctor, time, status).
- [ ] Data is injected and rendered in AppointmentCard or calendar events.
- [ ] At least 3–5 sample appointments are visible.

---

## Phase 10: Polish and Demo (Optional)

### SDUI-P10-01 — Demo all 6 screens

#### Functional Acceptance Criteria

- [ ] JSON specs exist for all 6 screens from `docs/VIEWS-SDUI-ANALYSIS.md`.
- [ ] Each spec renders without error.
- [ ] Specs are loadable via JSON spec selector.

---

### SDUI-P10-02 — Navigation between screens

#### Functional Acceptance Criteria

- [ ] Links or router allow moving between screens (e.g. Dashboard → Referral → Scheduler).
- [ ] Navigation actions in JSON (e.g. `navigate`) work.
- [ ] Browser back/forward behaves correctly (if using router).

---

### SDUI-P10-03 — Error handling

#### Functional Acceptance Criteria

- [ ] Invalid JSON shows user-friendly error (no white screen).
- [ ] Missing component type shows fallback or clear message.
- [ ] Network errors (data fetch) show retry or error message.

---

### SDUI-P10-04 — README and run instructions

#### Functional Acceptance Criteria

- [ ] README describes how to run the app (`npm install`, `npm run dev`).
- [ ] How to switch Doctor/Front Desk roles is documented.
- [ ] How to load different JSON specs is documented.
- [ ] Project structure and key files are briefly explained.
