# SDUI Runtime Renderer

A **Runtime UI Composition Engine** for EMR. Renders UI from JSON specs at runtime in React.

## Quick Start

- **Goals**: See [PROJECT_GOALS.md](./PROJECT_GOALS.md)
- **PRD**: See [docs/PRD.md](./docs/PRD.md)
- **Architecture**: See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- **Schema**: See [docs/SCHEMA-V1.md](./docs/SCHEMA-V1.md)
- **Agents**: See [AGENTS.md](./AGENTS.md)
- **Docs**: See [docs/README.md](./docs/README.md) (includes Functional AC, Technical AC)

## Project Structure

```
src/
├── renderer/       # Engine, registry, parser, validator, action-executor
├── components/     # Internal + wrappers (e.g. CalendarScheduler)
├── schema/         # Types, schema v1
└── scenarios/      # EMR scheduler JSON specs
```

## Pilot Use Case

EMR Scheduler/Calendar — role-based scenarios (Doctor, Front Desk) driven by server-sent JSON.
