# SDUI Project Goals

## Vision

Build a **bounded, intentional Runtime UI Composition Engine** for our EMR product. The renderer accepts JSON specs and renders UI dynamically in React, coexisting with normal static UI. First pilot: EMR Scheduler/Calendar.

**Phase 1**: UI-only test POC — JSON provided directly (static/mock). No backend.  
**Phase 2**: GraphQL for JSON generation.

---

## What We Want

1. **Renderer that accepts JSON** — Predefined object structure with actions, styles, layout. No visual builder.
2. **Data injection** — JSON defines structure + data binding (dataSource). Browser fetches real data at runtime; renderer injects into components. JSON does NOT carry data.
3. **Component registry** — Map JSON `type` to components from internal or external libs (MUI, AntD).
4. **Action abstraction** — JSON defines what happens; code executes it. Enables server-driven behavior changes.
5. **EMR Scheduler pilot** — Different scenarios (Doctor, Front Desk) from same calendar engine, different composition + actions.
6. **SDUI + static UI coexist** — Not everything is SDUI. Core flows can stay static; experiments and role-based screens use SDUI.

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
