# SDUI Demo — Presentation Guide

This guide helps you present the SDUI POC and explain its capabilities with concrete examples.

## Demo Flow

### 1. Landing Page (Home)

- **SDUI vs Static** — Header, toolbar, Search/Ask are static; main content is SDUI-driven.
- **Same Screen, Different Config** — Screen 6 shows Doctor vs Front Desk with the same layout, different JSON.
- **Add UI Without Redeploy** — Load new specs at runtime via the Demo toolbar.
- **Library Agnostic** — Components from MUI, internal, and FullCalendar; swap libs without changing specs.

### 2. Demo Mode (Floating Button)

Click the **purple science icon** (bottom-right) to open Demo Mode:

- **Show SDUI vs Static** — Labels on static parts (Header, toolbar, Search/Ask) and on the SDUI block.
- **Show Component Source** — Shows which library each component uses (MUI, internal, fullcalendar).
- **Load New Spec** — Load JSON from URL or paste JSON. UI updates without redeploy.

### 3. Presenting Key Points

| Point | How to Demonstrate |
|-------|--------------------|
| **SDUI vs Static** | Enable "Show SDUI vs Static", navigate to Screen 1. Point out grey "Static" labels for Header and Search/Ask, purple "SDUI" badge for main content. |
| **Same Screen, Different Config** | Go to Screen 6. Toggle Doctor View ↔ Front Desk. Same layout, different text and data; no code change. |
| **No Redeploy** | Open Demo → Load New Spec. Paste: `{"type":"Button","props":{"label":"New UI!","variant":"contained"},"action":{"type":"navigate","to":"/screen/1"}}`. Click Load. New button appears immediately. |
| **Library Agnostic** | Enable "Show Component Source". Show that Text, Button, etc. come from MUI; GreetingAvatar, AppointmentCard from internal; CalendarScheduler from FullCalendar. |

### 4. Sample Specs to Load

**Quick load:** In the Spec Loader dialog, click any sample chip (e.g. "S1: Card layout", "S6: Simple weekly") to load that spec instantly.

**Sample folder:** `src/views/sample/` — 2 examples per screen:
- Screen 1: `screen-1-card-layout.json`, `screen-1-compact-stats.json`
- Screen 2: `screen-2-row-cards.json`, `screen-2-alert-focus.json`
- Screen 3: `screen-3-card-message.json`, `screen-3-split-layout.json`
- Screen 4: `screen-4-status-success.json`, `screen-4-card-success.json`
- Screen 5: `screen-5-message-summary.json`, `screen-5-completion-card.json`
- Screen 6: `screen-6-simple-weekly.json`, `screen-6-cards-summary.json`

**Simple button (paste):**
```json
{"type":"Button","props":{"label":"New UI - No Redeploy!","variant":"contained"},"action":{"type":"navigate","to":"/screen/1"}}
```

## Actions in JSON Specs

Actions are defined in the JSON and work the same whether using the default spec or a loaded sample:

- **`action`** — Single action (e.g. `onClick`) for a component:
  ```json
  { "type": "Button", "props": { "label": "Go" }, "action": { "type": "navigate", "to": "/screen/2" } }
  ```
- **`actions`** — Map of event names to actions for multiple handlers.
- **Supported action types**: `navigate` (goes to route, clears loaded spec), `emit` (logs to console).

When you load a sample and click a button with `navigate`, the app navigates and clears the loaded spec so you see the correct screen content. You can add more actions in your JSON — they work the same way.

## Architecture Summary

- **Static**: Header, toolbar, SearchAskSection — hardcoded in the app.
- **SDUI**: Main content — rendered from JSON by `SDUIRenderer` via the registry.
- **Registry**: Maps component types (e.g. `Button`, `GreetingAvatar`) to implementations (MUI, internal, FullCalendar).
- **Spec**: JSON with `type`, `props`, `children`, `action`. Loaded at build time or from URL/JSON at runtime.
