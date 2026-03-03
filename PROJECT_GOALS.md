# SDUI Project Goals

## Vision

Build a **bounded, intentional Runtime UI Composition Engine** for our EMR product. The renderer accepts JSON specs and renders UI dynamically in React, coexisting with normal static UI. First pilot: **Chat interface** simulating two use cases.

**Phase 1**: UI-only POC — JSON from static files (simulating server). No backend.  
**Phase 2**: GraphQL for JSON generation; data binding from external API.

---

## What We Want

1. **Chat simulation** — User initiates (Hi/Hello/Show me my day) → server sends delta JSON → renderer injects into chat context.
2. **Renderer that accepts JSON** — Parse, validate (future), render. Internal + wrapped external (MUI, FullCalendar) components.
3. **Static vs Dynamic segregation** — Header, toolbar, Search/Ask = static. Chat content = SDUI (JSON-driven).
4. **Data binding** — JSON with embedded data (now). JSON + dataSource (future): client fetches from API, injects.
5. **Component registry** — Map `type` to components. Add new components/libs via wrappers.
6. **Action abstraction** — JSON defines actions; executor runs (navigate, api, emit, openForm, openDrawer).

---

## What We Don't Want

- Universal "render anything" engine
- Drag-and-drop builder (initially)
- Medical/PHI rules in JSON
- Arbitrary JS in JSON
- Replacing React — we extend it

---

## Success Definition

- Render **Doctor** and **Front Desk** scheduler views from two different JSON specs (showcase)
- 10–15 components in registry
- Action executor handles api, navigate, openForm, openDrawer
- Clear path to add more components and scenarios

---

## Reference

- Full context: See `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/SCHEMA-V1.md`
- Cursor rules: `.cursor/rules/` (project context, renderer patterns, EMR scheduler)
