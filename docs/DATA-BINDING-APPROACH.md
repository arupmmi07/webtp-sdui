# Data Binding Approach

How SDUI handles data: server ships it vs. client fetches and injects.

---

## Industry Approaches

### Airbnb (Ghost Platform)

- **Approach**: Server sends UI + data together in a single response
- **Sections** contain "the exact data to be displayed — already translated, localized, and formatted"
- Client takes section data and renders directly — no separate data fetch
- **Source**: [Airbnb Ghost Platform deep dive](https://medium.com/airbnb-engineering/a-deep-dive-into-airbnbs-server-driven-ui-system-842244c5f5)

### Netflix

- **Approach**: Server-driven; UDA (Unified Data Architecture) for unified data model
- GraphQL returns product info (layout, content) — not raw domain data
- Server controls what is displayed; clients render agnostically

### Apollo GraphQL SDUI

- **Principle**: "Return product info, not domain data"
- Server returns ready-to-display strings (formatted, localized)
- Client "handles pixels, not data" — minimal transformation
- **Source**: [Apollo SDUI Client Design](https://www.apollographql.com/docs/graphos/schema-design/guides/sdui/client-design)

### FormIO

- **Approach**: Schema and data are **separate**
- Form schema (structure) loaded once from URL or inline JSON
- Submission data loaded separately — via external API, on load, or on field change
- Supports: external data loading, calculated values, dynamic dropdown sources
- **Benefit**: Structure can be cached; data refreshed independently
- **Source**: FormIO external load examples, Submissions API

---

## Our Decision: Client-Side Data Binding

| Factor | Implication |
|--------|-------------|
| **PHI** | Cannot put patient names, appointments, referrals in JSON. Must fetch from secure APIs. |
| **Freshness** | Appointments and summaries change often. Client fetch keeps data current. |
| **FormIO pattern** | Structure (JSON) cached; data fetched when needed. Proven pattern. |
| **Hybrid option** | Non-PHI aggregates (e.g., "28 Due appointments") could be server-inline in Phase 2. PHI always client-fetched. |

### Implementation

```
JSON Spec (structure + dataSource + fieldMapping)
         ↓
Parser → SDUINode tree
         ↓
Data Injector: for each node with dataSource
  - Resolve dataSource (API path, context key)
  - Fetch data (client-side)
  - Map via fieldMapping to component props
         ↓
Renderer: pass resolved props to components
```

### JSON Example

```json
{
  "type": "AppointmentCard",
  "props": {
    "dataSource": "/api/appointments",
    "fieldMapping": {
      "patient": "patientName",
      "doctor": "providerName",
      "datetime": "slotStart",
      "status": "authorizationStatus"
    }
  }
}
```

Client fetches `/api/appointments`, maps fields, passes to `AppointmentCard`.

---

## When Server-Side Data Makes Sense

- No PHI (e.g., marketing content, feature flags)
- Content is static or changes infrequently
- Single round-trip preferred over freshness
- Airbnb/Netflix-style: server owns full experience

For EMR with PHI, client-side binding is the right choice.
