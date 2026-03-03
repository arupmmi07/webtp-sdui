# Source Structure

SDUI Chat POC: Simulates a chat interface where UI updates arrive as JSON from the server. Renderer uses internal + wrapped external (MUI, FullCalendar) components.

## Philosophy

- **Static vs Dynamic**: Header, toolbar, Search/Ask bar = static. Main chat content = SDUI (JSON-driven).
- **Chat context**: Starts blank. User initiates (Hi/Hello/Show me my day) → server sends first delta JSON → renderer injects into context.
- **Future**: Every piece of chat context loaded as JSON from server. New components/libs added via registry + wrappers.

## Structure

```
src/
├── renderer/           # SDUI engine
│   ├── SDUIRenderer.tsx   # Parse JSON → render nodes recursively
│   ├── registry.ts       # type → component (internal, MUI, fullcalendar)
│   └── ActionContext.tsx # Action executor (navigate, api, emit)
├── components/
│   ├── internal/       # GreetingAvatar, Message, DocumentPreviewCard, etc.
│   └── wrappers/       # MUI wrappers: Text, Button, Card, Row, Column, etc.
├── context/
│   ├── Flow4ChatContext.tsx  # Chat flow state, delta injection, buildChatSpec
│   └── DemoContext.tsx      # Demo mode: annotations, Load New Spec
├── views/
│   ├── flow1/          # Use case 1: delta-step1..5, scheduler
│   ├── flow2/          # Use case 2: delta-step1..7
│   └── sample/         # SpecLoaderDialog samples

├── pages/
│   └── ChatPage.tsx    # Main chat UI
└── components/demo/    # Dev tools: StaticSection, DemoToolbar, SpecLoaderDialog
```

## Data Binding

- **JSON with embedded data**: Supported. Props in JSON are passed directly.
- **JSON + dataSource (separate API)**: Documented in `docs/DATA-BINDING-APPROACH.md`. Not yet implemented.
- **Renderer**: Accepts `spec` (object or array of nodes). No schema validation yet.
