# Source Structure

Per `docs/ARCHITECTURE.md`:

```
src/
├── renderer/       # engine, registry, parser, validator, data-injector, action-executor
├── components/
│   ├── internal/  # Text, Row, Column, Card, Message, etc.
│   └── wrappers/   # CalendarSchedulerWrapper
├── schema/         # Types, schema v1
└── scenarios/
    └── scheduler/  # doctor-scheduler.json, front-desk-scheduler.json
```
