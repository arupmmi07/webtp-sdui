# SDUI Architecture

## 1. Core Components

### 1.1 Parser / Validator

- Validates JSON against schema v1
- Returns typed `SDUINode` tree or validation errors
- Handles unknown types (fallback or skip)

### 1.2 Component Registry

```typescript
type ComponentEntry = {
  component: React.ComponentType<any>;
  source: "internal" | "mui" | "antd" | "custom";
  allowedProps?: string[];
};

const registry: Record<string, ComponentEntry>;
```

- Maps `type` string → React component
- Supports internal and external libs
- No npm package names in JSON — registry is code-defined

### 1.3 Renderer Engine

- Recursive `renderNode(node)` function
- Binds actions to component props via `bindActions`
- Applies `style` to wrapper or component
- Renders `children` recursively

### 1.4 Data Injection Layer

- Reads `dataSource`, `fieldMapping` from JSON nodes
- Fetches data (API, context, props) at runtime
- Injects resolved data into component props before render
- **Critical**: JSON never contains data; only binding config

### 1.5 Action Executor

- Central handler for all action types
- Injects `onClick`, `onEventClick`, etc. from JSON `action`
- EMR-aware for openForm, openDrawer, openWizard

---

## 2. Data Flow

```
JSON Spec (Phase 1: static/mock | Phase 2: GraphQL)
    ↓
parse(spec) → SDUINode[]
    ↓
validate(nodes) → valid | errors
    ↓
resolveDataSources(nodes) → fetch/inject data (browser does this)
    ↓
renderNode(root, injectedData) → React elements
    ↓
User interaction → actionExecutor.execute(action)
```

### 2.1 Data Binding: Client-Side (Decision)

**We use client-side data binding** — JSON has structure + `dataSource`; client fetches and injects.

**Why not server-side (Airbnb/Netflix style)?** PHI cannot go in JSON. Appointments, patient names, referrals must be fetched from secure APIs by the client.

**Industry**: Airbnb sends data with UI; FormIO separates schema and data. We follow FormIO-style for PHI screens. See `docs/DATA-BINDING-APPROACH.md`.

**Flow**: JSON defines `dataSource` + `fieldMapping` → Data Injector fetches → Renderer passes resolved props to components.

---

## 3. Folder Structure (Proposed)

```
src/
├── renderer/
│   ├── engine.tsx          # renderNode, bindActions
│   ├── registry.ts         # Component registry
│   ├── parser.ts           # JSON → SDUINode
│   ├── validator.ts        # Schema validation
│   ├── data-injector.ts    # Resolve dataSource, fetch, inject
│   └── action-executor.ts  # Action handling
├── components/
│   ├── internal/           # Text, Row, Column, Card, etc.
│   └── wrappers/           # CalendarSchedulerWrapper
├── schema/
│   └── v1.ts               # Types, schema definition
└── views/
    ├── flow1/              # Use case 1: deltas + scheduler
    │   └── scheduler/       # doctor-scheduler.json, front-desk-scheduler.json
    ├── flow2/              # Use case 2: deltas
    └── sample/              # SpecLoaderDialog samples
```

---

## 4. Integration Points

### 4.1 With EMR Backend

- **Phase 1**: No backend. JSON from static files / mock.
- **Phase 2**: GraphQL returns SDUI spec per user/role/context
- Spec includes `CalendarScheduler` config + actions + data binding hints
- **Data (appointments) always fetched by browser** — never in JSON. Renderer injects at runtime.

### 4.2 With Existing App

- `SDUIRenderer` is a React component
- Receives `spec` prop (object or fetch URL)
- Renders inside static layout (Header, Footer)
