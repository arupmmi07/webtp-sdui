# SDUI Runtime Renderer — Technical Acceptance Criteria (TA)

> **Owner:** SDUI Project Lead  
> **Workstream:** SDUI POC  
> **Lifecycle:** Active — Phase 1 POC through Doctor + Front Desk showcase

---

## How to Use

1. Review `functional-ac.md` for business scope and stakeholder-visible acceptance criteria.
2. Use this document as the technical implementation plan for each story.
3. Execute stories in phase order; dependencies are noted in `docs/EXECUTION-PLAN.md`.

---

## Current State (Pre-Implementation)

- Project folder structure exists: `src/renderer`, `components`, `schema`, `scenarios`.
- Documentation: PRD, ARCHITECTURE, SCHEMA-V1, COMPONENT-STRATEGY, EXECUTION-PLAN, VIEWS-SDUI-ANALYSIS.
- No Vite/React app yet; no dependencies installed.
- Views (6 PNGs) define target UI; JSON specs will be authored to match.

---

## Repo Guardrails (Always Applies)

- Use TypeScript strict mode; avoid `any` where possible.
- Use MUI components for UI (no raw HTML controls for base components).
- Follow `docs/COMPONENT-STRATEGY.md` for component registry mapping.
- No PHI in JSON; data binding is client-side only.
- Keep renderer logic in `src/renderer/`; components in `src/components/`.

---

## Phase 1: Project Setup

### SDUI-P1-01 — Initialize React + TypeScript + Vite

#### Technical Goal

Create a Vite + React + TypeScript project with a minimal runnable app.

#### Proposed Technical Approach

1. Run `npm create vite@latest sdui -- --template react-ts` (or `pnpm create vite`).
2. Enable strict mode in `tsconfig.json`.
3. Add ESLint: `npm init @eslint/config` or extend `eslint.config.js` for React + TypeScript.
4. Ensure `npm run dev` starts dev server and `npm run build` produces a valid build.

#### Deliverables

- `package.json` with scripts: `dev`, `build`, `preview`.
- `tsconfig.json` with `strict: true`.
- `vite.config.ts` with React plugin.
- `src/App.tsx` and `src/main.tsx` with minimal placeholder.

---

### SDUI-P1-02 — Install dependencies (MUI, FullCalendar, Emotion)

#### Technical Goal

Install MUI, FullCalendar, and Emotion with compatible versions.

#### Proposed Technical Approach

1. Install MUI core:
   ```bash
   npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
   ```
2. Install FullCalendar:
   ```bash
   npm install @fullcalendar/react @fullcalendar/core @fullcalendar/daygrid @fullcalendar/timegrid
   ```
3. Verify peer dependencies; fix any mismatches.
4. Use `^5` for MUI, `^6` for FullCalendar (or latest stable).

#### Deliverables

- `package.json` with all dependencies.
- No peer dependency errors on `npm install`.

---

### SDUI-P1-03 — Configure folder structure

#### Technical Goal

Create folder structure per `docs/ARCHITECTURE.md`.

#### Proposed Technical Approach

1. Create directories:
   - `src/renderer/`
   - `src/components/internal/`
   - `src/components/wrappers/`
   - `src/schema/`
   - `src/scenarios/scheduler/`
2. Add `.gitkeep` or placeholder files if needed for empty dirs.
3. Optionally add `src/views/` for static view components if needed.

#### Deliverables

- Folder structure matches architecture doc.

---

### SDUI-P1-04 — Configure path aliases

#### Technical Goal

Enable `@/` (or similar) imports for cleaner paths.

#### Proposed Technical Approach

1. In `tsconfig.json`:
   ```json
   {
     "compilerOptions": {
       "baseUrl": ".",
       "paths": {
         "@/*": ["src/*"]
       }
     }
   }
   ```
2. In `vite.config.ts`:
   ```ts
   resolve: {
     alias: {
       '@': path.resolve(__dirname, './src'),
     },
   },
   ```
3. Ensure `path` is imported if using Node `path`.

#### Deliverables

- Imports like `import { X } from '@/renderer/engine'` resolve.
- Build succeeds with path aliases.

---

### SDUI-P1-05 — Add MUI ThemeProvider

#### Technical Goal

Wrap app with MUI ThemeProvider for consistent styling.

#### Proposed Technical Approach

1. In `src/main.tsx` or `App.tsx`:
   ```tsx
   import { ThemeProvider, createTheme } from '@mui/material/styles';
   const theme = createTheme({ palette: { mode: 'light' } });
   <ThemeProvider theme={theme}>
     <App />
   </ThemeProvider>
   ```
2. Use CssBaseline for reset (optional).

#### Deliverables

- ThemeProvider wraps app.
- MUI components render with consistent styling.

---

## Phase 2: Creating Components

### SDUI-P2-01 — Register MUI primitives

#### Technical Goal

Create wrappers and register Text, Button, Card, Alert, Row, Column, Spacer, Divider.

#### Proposed Technical Approach

1. **Text**: Wrap `Typography`; map `value` → `children`, `variant` → `variant`.
2. **Button**: Wrap `Button`; map `label` → `children`; pass through `variant`, `color`.
3. **Card**: Wrap `Card` + `CardContent`; render `children` in CardContent.
4. **Alert**: Wrap `Alert`; map `message` → `children`, `severity` from props.
5. **Row**: `Stack direction="row"`; pass `children`, `spacing`, `sx`.
6. **Column**: `Stack direction="column"`; same.
7. **Spacer**: `Box flex={1}` or `Box sx={{ flex: 1 }}`.
8. **Divider**: `Divider` directly.

Location: `src/components/internal/` or `src/components/wrappers/` for each wrapper.

#### Deliverables

- Wrapper components for each primitive.
- All registered in `registry.ts` (to be created in P2-10).

---

### SDUI-P2-02 — Register Select/Dropdown

#### Technical Goal

Map JSON `Dropdown`/`Select` to MUI Select with options from JSON.

#### Proposed Technical Approach

1. Accept props: `options: { value: string; label: string }[]`, `value`, `onChange`, `label`.
2. Use MUI `Select` with `MenuItem` for each option.
3. `onChange` triggers `actionExecutor.execute(action)` when action is provided.
4. Support controlled mode via `value` prop.

#### Deliverables

- `Dropdown` / `Select` component.
- Registered in registry.

---

### SDUI-P2-03 — Register IconButton, SegmentedControl

#### Technical Goal

IconButton for message actions; SegmentedControl for view toggle.

#### Proposed Technical Approach

1. **IconButton**: Use MUI `IconButton`; map `icon` (string) to MUI icon (e.g. via `@mui/icons-material` lookup or a map).
2. **SegmentedControl**: Use MUI `ToggleButtonGroup`; options from JSON `options: string[]` or `{ value, label }[]`; `value` and `onChange` from props.

#### Deliverables

- Both components implemented and registered.

---

### SDUI-P2-04 — Build Message component

#### Technical Goal

Chat-style bubble: avatar, timestamp, content, optional action icons.

#### Proposed Technical Approach

1. Layout: `Card` or `Paper` with `display: flex`, avatar on left.
2. Avatar: MUI `Avatar` (or placeholder icon).
3. Timestamp: `Typography variant="caption"`.
4. Content: `Typography` with `children` from props.
5. Action icons: `Row` of `IconButton` with `action` from props.
6. Props: `avatar?`, `timestamp`, `content`, `actions?: { icon, action }[]`.

#### Deliverables

- `Message.tsx` in `src/components/internal/`.
- Registered as `Message`.

---

### SDUI-P2-05 — Build StatusMessage component

#### Technical Goal

Success/error/warning message with icon and text.

#### Proposed Technical Approach

1. Use MUI `Alert` with `severity`: `success` | `error` | `warning`.
2. Icon: MUI `CheckCircle`, `Error`, `Warning` (or use Alert's built-in).
3. Props: `message`, `severity`, `icon?` (optional override).

#### Deliverables

- `StatusMessage.tsx`.
- Registered as `StatusMessage`.

---

### SDUI-P2-06 — Build SummaryStat component

#### Technical Goal

Row of items: label + value, optional action.

#### Proposed Technical Approach

1. Use `Stack direction="row"` with `Divider` between items.
2. Each item: `Typography` for label + value.
3. Props: `items: { label: string; value: string; action?: Action }[]`.
4. Optional "+8 More" as last item with `action`.

#### Deliverables

- `SummaryStat.tsx`.
- Registered as `SummaryStat`.

---

### SDUI-P2-07 — Build WeeklyHeader component

#### Technical Goal

Date range + count badge.

#### Proposed Technical Approach

1. Layout: `Stack` with `Typography` for date range and `Chip` or `Badge` for count.
2. Props: `dateRange: string`, `count: number`.
3. Optional: calendar icon from MUI icons.

#### Deliverables

- `WeeklyHeader.tsx`.
- Registered as `WeeklyHeader`.

---

### SDUI-P2-08 — Build AppointmentCard component

#### Technical Goal

Card with patient, doctor, insurance, time, status.

#### Proposed Technical Approach

1. Use MUI `Card` with `CardContent`.
2. Fields: `patient`, `doctor`, `insurance`, `datetime`, `status`.
3. Status: map to color (Valid=green, Expiring=orange, Invalid=red, High No-Show=badge).
4. Use `Chip` or `Typography` with `color` for status.
5. Optional `action` for click (openDrawer).

#### Deliverables

- `AppointmentCard.tsx`.
- Registered as `AppointmentCard`.

---

### SDUI-P2-09 — Build CalendarScheduler wrapper

#### Technical Goal

Wrap FullCalendar; config from JSON props; actions from JSON.

#### Proposed Technical Approach

1. Import FullCalendar:
   ```tsx
   import FullCalendar from '@fullcalendar/react';
   import dayGridPlugin from '@fullcalendar/daygrid';
   import timeGridPlugin from '@fullcalendar/timegrid';
   ```
2. Props from JSON: `view`, `slotDuration`, `workingHours`, `allowOverbooking`, `groupBy` (optional).
3. Map to FullCalendar props: `initialView`, `slotDuration`, `businessHours`, `editable`.
4. `onSlotClick` → `dateClick`; `onEventClick` → `eventClick`; `onEventDrag` → `eventDrop`.
5. Bind each to `actionExecutor.execute(action)`.
6. Events: pass via `events` prop (from data injection or parent).

#### Deliverables

- `CalendarSchedulerWrapper.tsx` in `src/components/wrappers/`.
- Registered as `CalendarScheduler`.

---

### SDUI-P2-10 — Create component registry

#### Technical Goal

Single registry mapping `type` → `ComponentEntry`.

#### Proposed Technical Approach

1. Define `ComponentEntry` type (see P4-04).
2. Create `registry.ts`:
   ```ts
   const registry: Record<string, ComponentEntry> = {
     Text: { component: TextWrapper, source: 'mui' },
     Button: { component: ButtonWrapper, source: 'mui' },
     // ... all components
   };
   export function getComponent(type: string): ComponentEntry | null {
     return registry[type] ?? null;
   }
   ```
3. Export registry and getter.

#### Deliverables

- `src/renderer/registry.ts` (or `src/components/registry.ts`).
- All components from P2-01–P2-09 registered.

---

## Phase 3: Demo Environment

### SDUI-P3-01 — Create demo JSON fixtures

#### Technical Goal

Valid JSON specs for testing.

#### Proposed Technical Approach

1. Create `doctor-scheduler.json` and `front-desk-scheduler.json` in `src/scenarios/scheduler/`.
2. Add `simple-card.json`, `simple-button.json` for static view tests.
3. Use schema from Phase 4; keep fixtures minimal but valid.
4. Import as static or fetch via `fetch()` in dev.

#### Deliverables

- `doctor-scheduler.json`, `front-desk-scheduler.json` (minimal).
- 1–2 additional fixtures for static views.

---

### SDUI-P3-02 — Create demo page route

#### Technical Goal

Route that renders SDUIRenderer with a spec.

#### Proposed Technical Approach

1. Add React Router (or use hash routing if minimal).
2. Route: `/demo` or `/sdui-demo`.
3. Page component: loads default spec (e.g. doctor-scheduler), passes to `SDUIRenderer`.
4. Optional: `useState` for spec, update when spec changes.

#### Deliverables

- `DemoPage.tsx` with route.
- `SDUIRenderer` receives spec and renders.

---

### SDUI-P3-03 — Add role switcher (Doctor/Front Desk)

#### Technical Goal

Toggle that loads doctor or front-desk spec.

#### Proposed Technical Approach

1. Add `ToggleButtonGroup` or `SegmentedControl` with "Doctor" | "Front Desk".
2. On change: `setSpec(doctorSpec)` or `setSpec(frontDeskSpec)`.
3. Specs loaded via `import` or `fetch` from `scenarios/scheduler/` at build time.

#### Deliverables

- Role switcher UI.
- Correct spec loaded per selection.

---

### SDUI-P3-04 — Add JSON spec selector

#### Technical Goal

Dropdown/tabs to load different specs.

#### Proposed Technical Approach

1. List of spec names + URLs or imported modules.
2. `Select` or `Tabs` to choose.
3. On change: load spec and pass to `SDUIRenderer`.
4. Include: Doctor, Front Desk, Simple Card, Simple Button (at minimum).

#### Deliverables

- Spec selector UI.
- Multiple specs loadable.

---

## Phase 4: TypeScript Types for Renderer Schema

### SDUI-P4-01 — Define SDUINode type

#### Technical Goal

Canonical `SDUINode` type for parser output.

#### Proposed Technical Approach

```ts
export interface SDUINode {
  type: string;
  props?: Record<string, unknown>;
  style?: Record<string, unknown>;
  action?: Action;
  children?: SDUINode[];
}
```

Location: `src/schema/v1.ts`.

---

### SDUI-P4-02 — Define Action types

#### Technical Goal

Discriminated union for all action types.

#### Proposed Technical Approach

```ts
export type Action =
  | { type: 'api'; endpoint: string }
  | { type: 'navigate'; to: string }
  | { type: 'emit'; event: string }
  | { type: 'openForm'; form: string }
  | { type: 'openDrawer'; panel: string }
  | { type: 'openWizard'; flow: string };
```

---

### SDUI-P4-03 — Define dataSource / fieldMapping types

#### Technical Goal

Types for data binding.

#### Proposed Technical Approach

```ts
export interface DataBindingConfig {
  dataSource: string;  // API path or context key
  fieldMapping?: Record<string, string>;  // fetched field → component prop
}
```

Extend `SDUINode.props` to allow these; or add to `SDUINode` as optional top-level fields.

---

### SDUI-P4-04 — Define ComponentEntry type

#### Technical Goal

Registry entry type.

#### Proposed Technical Approach

```ts
export type ComponentSource = 'internal' | 'mui' | 'fullcalendar';

export interface ComponentEntry {
  component: React.ComponentType<any>;
  source: ComponentSource;
  allowedProps?: string[];
}
```

---

### SDUI-P4-05 — Export schema types

#### Technical Goal

Single export surface for schema.

#### Proposed Technical Approach

1. `src/schema/v1.ts` contains all types.
2. `src/schema/index.ts` re-exports from v1.
3. Or: single `schema.ts` with all types.

#### Deliverables

- `import { SDUINode, Action, ComponentEntry } from '@/schema'` works.

---

## Phase 5: Renderer Tasks

### SDUI-P5-01 — Implement parser

#### Technical Goal

JSON → SDUINode tree.

#### Proposed Technical Approach

1. `parse(spec: unknown): SDUINode | SDUINode[]`
2. If `spec` is array, parse each element; else parse single object.
3. Recursively parse `children` if present.
4. Validate `type` is string; use type assertion or runtime check for structure.
5. Return typed tree or throw `ParseError` with message.

#### Deliverables

- `src/renderer/parser.ts` with `parse` function.

---

### SDUI-P5-02 — Implement validator

#### Technical Goal

Validate parsed nodes before render.

#### Proposed Technical Approach

1. `validate(nodes: SDUINode[]): { valid: boolean; errors: string[] }`
2. Check: each node has `type`; known types (optional, can allow unknown with fallback).
3. Check: required props per type (optional for Phase 1).
4. Return errors array; `valid: errors.length === 0`.

#### Deliverables

- `src/renderer/validator.ts`.

---

### SDUI-P5-03 — Implement renderNode (recursive)

#### Technical Goal

Core render loop.

#### Proposed Technical Approach

1. `renderNode(node: SDUINode, context?: RenderContext): ReactNode`
2. Lookup: `getComponent(node.type)`.
3. If not found: return null or fallback (per P5-07).
4. Merge props: `node.props` + `bindActions(node.props, node.action)` + resolved data.
5. Apply `node.style` via `sx` or wrapper.
6. Children: `node.children?.map(child => renderNode(child, context))`.
7. Return `React.createElement(Component, props, children)`.

#### Deliverables

- `src/renderer/engine.tsx` with `renderNode`.

---

### SDUI-P5-04 — Implement bindActions

#### Technical Goal

Map action → onClick handler.

#### Proposed Technical Approach

1. `bindActions(props: object, action?: Action): object`
2. If no action, return props.
3. Else: `return { ...props, onClick: () => actionExecutor.execute(action) }`.
4. For components with multiple actions (e.g. CalendarScheduler): pass `onSlotClick`, `onEventClick` as separate handlers; each maps to its action.

#### Deliverables

- `bindActions` in `engine.tsx` or `action-executor.ts`.

---

### SDUI-P5-05 — Implement action executor

#### Technical Goal

Execute each action type.

#### Proposed Technical Approach

1. `execute(action: Action): void | Promise<void>`
2. Switch on `action.type`:
   - `api`: `fetch(action.endpoint)` (or injected API client).
   - `navigate`: `window.location.href = action.to` or `router.push(action.to)`.
   - `emit`: `window.dispatchEvent(new CustomEvent(action.event))`.
   - `openForm`, `openDrawer`, `openWizard`: call injected handler (e.g. `handlers.openForm(action.form)`).
3. For Phase 1: stub handlers that `console.log` or show toast.
4. Make executor injectable for testing.

#### Deliverables

- `src/renderer/action-executor.ts`.

---

### SDUI-P5-06 — Implement SDUIRenderer component

#### Technical Goal

Main React component.

#### Proposed Technical Approach

1. `SDUIRenderer({ spec }: { spec: unknown })`
2. Parse: `const nodes = parse(spec)`.
3. Validate: `const { valid, errors } = validate(nodes)`.
4. If invalid: render error UI or null.
5. Else: render `nodes.map(node => renderNode(node))` wrapped in Fragment or div.
6. Handle async: if data injector is async, use `useState` + `useEffect` for loading.

#### Deliverables

- `src/renderer/SDUIRenderer.tsx` or `engine.tsx` exporting `SDUIRenderer`.

---

### SDUI-P5-07 — Handle unknown component types

#### Technical Goal

No crash on unknown type.

#### Proposed Technical Approach

1. In `renderNode`: if `getComponent(node.type)` returns null, return `null` or a fallback.
2. Fallback option: `<Box sx={{ p: 1, bgcolor: 'grey.200' }}>Unknown: {node.type}</Box>` (dev only).
3. Optional: log `console.warn` in dev.

#### Deliverables

- `renderNode` handles unknown types gracefully.

---

### SDUI-P5-08 — Apply style prop

#### Technical Goal

Pass `node.style` to components.

#### Proposed Technical Approach

1. Merge `node.style` into props as `sx` if using MUI.
2. Or wrap in `<Box sx={node.style}>` around the component.
3. Ensure style values are valid (numbers for px, strings for units).

#### Deliverables

- `style` applied correctly in render.

---

## Phase 6: Static View Stories

#### Technical Goal

End-to-end validation of each component via JSON.

#### Proposed Technical Approach

For each story, create a minimal JSON fixture and verify it renders. Example for Text:

```json
{ "type": "Text", "props": { "value": "Hello" } }
```

Pass to `SDUIRenderer`; assert "Hello" is visible. Repeat for each component type.

#### Testing Requirements

- Manual or automated: load fixture, verify component renders.
- Optional: React Testing Library tests for each component type.

---

## Phase 7: AppShell and Renderer Integration

### SDUI-P7-01 through SDUI-P7-05

#### Technical Goal

AppShell layout + SDUIRenderer integration.

#### Proposed Technical Approach

1. **AppShell**: `Box` or `Stack` with `height: 100vh`, header (fixed), main (flex: 1, overflow auto), footer (fixed).
2. **Header**: `AppBar` or custom `Box` with logo, search `TextField`, icons, `Avatar`.
3. **Footer**: `Box` with search input, nav icons, SummaryStat slot.
4. **Integration**: `main` contains `SDUIRenderer spec={spec}`.
5. **ScreenLayout**: `function ScreenLayout({ spec }) { return <AppShell><SDUIRenderer spec={spec} /></AppShell>; }`.

#### Deliverables

- `AppShell.tsx`, `Header.tsx`, `Footer.tsx`, `ScreenLayout.tsx`.

---

## Phase 8: API and Data Loading

### SDUI-P8-01 — Implement data injector

#### Technical Goal

Resolve dataSource, fetch, map, inject.

#### Proposed Technical Approach

1. `injectData(node: SDUINode, context: InjectContext): Promise<SDUINode>`
2. If `node.props?.dataSource`:
   - Fetch from `dataSource` (API or context).
   - Apply `fieldMapping` to map response to props.
   - Return node with merged props.
3. If `node.children`:
   - Recursively inject data for each child.
4. Use `async`/`await`; renderer must handle loading state.

#### Deliverables

- `src/renderer/data-injector.ts`.

---

### SDUI-P8-02 — Support dataSource in parser

#### Technical Goal

Parser preserves dataSource/fieldMapping.

#### Proposed Technical Approach

- Parser already passes through `props`; no change if `dataSource` is in `props`.
- Ensure schema types include `dataSource` and `fieldMapping` in node props.

---

### SDUI-P8-03 — Create mock API layer

#### Technical Goal

Mock endpoints for Phase 1.

#### Proposed Technical Approach

1. Option A: Vite proxy to static JSON files.
2. Option B: MSW (Mock Service Worker) to intercept `/api/*` and return fixtures.
3. Option C: Simple Express server (if not using Vite proxy).
4. Mock data: `appointments.json`, `day-summary.json` with realistic structure.

#### Deliverables

- Mock endpoints return JSON compatible with fieldMapping.
- Easy to swap for real API in Phase 2.

---

### SDUI-P8-04 — Inject data into components

#### Technical Goal

Renderer passes resolved data to components.

#### Proposed Technical Approach

1. Before `renderNode`, run `injectData` for nodes with dataSource.
2. Use `useEffect` + `useState` for async; show loading until resolved.
3. Pass resolved props to `renderNode` (or merge in renderNode).

---

### SDUI-P8-05 — Handle loading/error states

#### Technical Goal

Loading spinner; error message.

#### Proposed Technical Approach

1. Loading: `CircularProgress` or skeleton while `injectData` is pending.
2. Error: `Alert severity="error"` with message; optional retry button.
3. Wrap data-dependent render in error boundary or try/catch.

---

## Phase 9: Doctor and Front Desk Scenarios

### SDUI-P9-01, P9-02 — Create JSON specs

#### Technical Goal

Valid, complete specs for both roles.

#### Proposed Technical Approach

1. **doctor-scheduler.json**: Root with `CalendarScheduler` or `Column` containing scheduler + toolbar. Props: `view: "timeGridDay"`, `slotDuration: "00:15:00"`, `allowOverbooking: false`. Actions: `onSlotClick`, `onEventClick`.
2. **front-desk-scheduler.json**: Same structure; `view: "timeGridWeek"`, `groupBy: "resource"` (if supported), `allowOverbooking: true`. Actions: `onSlotClick` (openWizard), `onEventDrag` (reschedule).

#### Deliverables

- Both JSON files valid and loadable.

---

### SDUI-P9-03 through P9-06

#### Technical Goal

Render both schedulers; role switcher; mock data.

#### Proposed Technical Approach

- P9-03, P9-04: Load spec, pass to SDUIRenderer; verify FullCalendar renders with correct config.
- P9-05: Role switcher already in P3-03; ensure it loads correct spec.
- P9-06: Wire dataSource in scheduler/appointment nodes to mock API; verify data injector fetches and passes to AppointmentCard or FullCalendar events.

---

## Phase 10: Polish and Demo

#### Technical Goal

Full demo; navigation; error handling; docs.

#### Proposed Technical Approach

1. **P10-01**: Author JSON for all 6 screens; add to spec selector.
2. **P10-02**: Add React Router; `navigate` action uses `router.push`.
3. **P10-03**: Error boundary around SDUIRenderer; invalid JSON shows Alert.
4. **P10-04**: Update README with run instructions, role switcher, spec selector.

---

## Testing Requirements (Summary)

- Unit tests: parser, validator, action executor (optional but recommended).
- Component tests: renderNode with mock registry (optional).
- Integration: load spec, verify output (manual or E2E).
- Accessibility: keyboard nav, focus, labels (Phase 2 or polish).

---

## Risks / Mitigations

| Risk | Mitigation |
|------|-------------|
| FullCalendar config mismatch | Start with minimal config; expand as needed. |
| Data injector async complexity | Use simple `useEffect` + `useState`; defer complex optimizations. |
| Registry drift | Single registry file; enforce registration in P2-10. |
| JSON schema evolution | Document in SCHEMA-V1; version if needed. |
