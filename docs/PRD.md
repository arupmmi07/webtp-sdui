# SDUI Runtime Renderer — Product Requirements Document

## 1. Overview

### 1.1 Purpose

Build a **Runtime UI Composition Engine** that renders UI from JSON specs at runtime. The primary pilot use case is an EMR Scheduler/Calendar where layout, actions, and behavior vary by role and context without app redeployment.

### 1.2 Phase Strategy

| Phase | Scope | JSON Source |
|-------|-------|--------------|
| **Phase 1** | UI-only test POC | JSON provided directly (static files, mock, hardcoded) |
| **Phase 2** | Backend integration | GraphQL for JSON generation |

Phase 1 proves the renderer works with static JSON. Phase 2 adds server-driven spec generation.

### 1.2 What We Are NOT Building

- Universal "render anything" UI engine
- Visual drag-and-drop builder
- Cross-platform renderer (Web first; mobile later if needed)
- Replacement for React/Angular — we extend them

---

## 2. Goals & Success Criteria

### 2.1 Goals

1. **Renderer only**: Accept predefined JSON structure and render in React
2. **Component registry**: Support internal + external lib components (MUI, AntD, etc.)
3. **Action system**: Decouple UI from behavior via abstract actions
4. **EMR Scheduler pilot**: Prove SDUI with Doctor vs Front Desk scenarios
5. **Coexistence**: SDUI screens alongside static React UI

### 2.2 Scheduler Showcase Requirement (Critical)

**We must articulate two distinct scenarios in the scheduler view to demonstrate SDUI benefits:**

| Scenario | Role | JSON Spec | Purpose |
|----------|------|-----------|---------|
| **Doctor View** | Doctor | `doctor-scheduler.json` | Day view, no overbooking, limited actions |
| **Front Desk View** | Front Desk | `front-desk-scheduler.json` | Week view, overbooking allowed, full booking flow |

Same renderer, same `CalendarScheduler` component — **different JSON = different UI and behavior**. This showcases:
- No app redeploy to change role-based experience
- Server controls layout, actions, and rules per role
- Single codebase, multiple experiences

### 2.3 Success Criteria

- Render **Doctor** and **Front Desk** scheduler scenarios from two different JSON specs (no code changes between them)
- Support 10–15 core components in registry
- Action executor handles api, navigate, openForm, openDrawer
- No app redeploy for UI/action changes driven by server spec

---

## 3. Scope

### 3.1 In Scope (MVP)

| Item | Description |
|------|-------------|
| JSON schema v1 | Explicit, boring schema for components, props, actions, styles |
| Parser/validator | Validate incoming JSON against schema |
| Renderer engine | Recursive renderer + component registry |
| Action executor | api, navigate, emit, openForm, openDrawer |
| Core components | Text, Row, Column, Button, Card, CalendarScheduler, Toolbar, Drawer, Banner, Select, Divider |
| EMR scenarios | Doctor daily view, Front Desk booking mode |

### 3.2 Out of Scope (MVP)

| Item | Reason |
|------|--------|
| Visual builder | Renderer only; authoring later |
| Cross-platform | Web (React) first |
| Conditional visibility / feature flags | Phase 2 |
| Theming | Phase 2 |
| Offline/caching | Phase 2 |

---

## 4. Architecture

### 4.1 High-Level Flow

```
Server (EMR Backend)
  ├─ User Context (role, dept, permissions)
  ├─ Schedule Rules Engine
  └─ SDUI Spec Generator
           ↓
     JSON UI Spec
           ↓
    Parser / Validator
           ↓
    SDUI Renderer (React)
           ↓
   Component Registry
           ↓
   React Components (internal + MUI/AntD)
```

### 4.2 Component Types

| Type | Example | Source |
|------|---------|--------|
| Native primitives | Text, Row, Column, Spacer | Internal |
| Composite | Card, Section, Toolbar | Internal |
| External | MUI Button, AntD Table | External libs |

### 4.3 Data Binding Approach (Critical)

**Decision: Client-side data binding** — JSON defines structure + `dataSource` hints; browser fetches and injects.

#### Industry Approaches

| Company / Tool | Approach | Notes |
|----------------|----------|-------|
| **Airbnb (Ghost Platform)** | Server sends UI + data together | Sections contain "exact data to be displayed — already translated, localized, and formatted." Single response. Client just renders. |
| **Netflix** | Server-driven, unified data | UDA (Unified Data Architecture) — server controls structure and content. GraphQL returns product info, not raw domain data. |
| **Apollo GraphQL SDUI** | Server returns product info | "Return product info, not domain data." Server sends ready-to-display strings. Client "handles pixels, not data." |
| **FormIO** | Schema + data separate | Form schema (structure) loaded once; submission data loaded separately via external API or on field change. Decoupled. |

#### Why We Choose Client-Side Binding

1. **PHI constraint**: We cannot put PHI (patient names, appointments, referrals) in JSON. Data must be fetched by the client from secure APIs.
2. **Freshness**: Appointments, referrals, and day summaries change frequently. Client fetch keeps data current.
3. **FormIO-style flexibility**: Structure can be cached; data can be refreshed independently.
4. **Hybrid option**: For non-PHI aggregates (e.g., "28 appointments"), server *could* send inline in Phase 2 if desired. For PHI, client fetch is mandatory.

#### Implementation

- **JSON** = structure + `dataSource` + `fieldMapping` (binding config only)
- **Client** = fetches from API/context, injects into components at render
- **Renderer** = resolves `dataSource`, calls data layer, passes resolved props to components

### 4.4 SDUI + Static Coexistence

```tsx
function Screen() {
  return (
    <>
      <Header />                    {/* Static */}
      <SDUIRenderer spec={spec} />  {/* Runtime */}
      <Footer />                    {/* Static */}
    </>
  );
}
```

---

## 5. JSON Schema (v1)

### 5.1 Node Structure

```json
{
  "type": "Card",
  "props": { "elevation": 2 },
  "style": { "padding": 16 },
  "action": { "type": "api", "endpoint": "/pay" },
  "children": [
    { "type": "Text", "props": { "value": "Order Summary" } },
    { "type": "Button", "props": { "label": "Pay Now" }, "action": { "type": "api", "endpoint": "/pay" } }
  ]
}
```

### 5.2 Action Types

| Type | Payload | Purpose |
|------|---------|---------|
| `api` | `{ endpoint: string }` | Call API |
| `navigate` | `{ to: string }` | Route change |
| `emit` | `{ event: string }` | Custom event |
| `openForm` | `{ form: string }` | EMR form |
| `openDrawer` | `{ panel: string }` | EMR drawer |
| `openWizard` | `{ flow: string }` | EMR wizard |

### 5.3 Layout

Prefer logical layout (Row, Column, Grid). Absolute x-y only if explicitly required.

---

## 6. EMR Scheduler Scenarios (Showcase Requirement)

**Two distinct JSON specs** — same renderer, different experience. This is the primary POC demonstration.

### 6.1 Doctor View (`doctor-scheduler.json`)

- View: day
- Slot duration: 15m
- No overbooking
- Actions: openForm (new appointment), openDrawer (details)
- Limited controls (no bulk operations)

### 6.2 Front Desk View (`front-desk-scheduler.json`)

- View: week
- Group by: doctor
- Overbooking allowed
- Actions: openWizard (book flow), rescheduleWithConfirmation
- Full booking controls, availability display

---

## 7. Constraints & Guardrails

- **No PHI in JSON**: SDUI does not fetch or display PHI directly
- **No medical rules in JSON**: Validations stay in code
- **No arbitrary JS**: JSON is data only
- **Versioned schema**: Support fallback for unknown nodes

---

## 8. Effort Estimate

| Phase | Scope | Effort |
|-------|-------|--------|
| MVP | Renderer + 10–15 components + 2 scenarios | 3–4 weeks, 1 senior FE |
| Phase 2 | Conditional visibility, theming, validation | +4–6 weeks |

---

## 9. Open Questions

- [ ] FullCalendar vs custom grid for CalendarScheduler
- [ ] Schema versioning strategy
- [ ] Data injection API design (how components receive injected data)
