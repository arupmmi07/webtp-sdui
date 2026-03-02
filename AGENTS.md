# SDUI Project — Agent Defaults

Use this file to orient AI agents working on this project.

## Quick Context

- **What**: Runtime UI Composition Engine for EMR. Renders JSON specs in React.
- **Pilot**: EMR Scheduler (Doctor vs Front Desk scenarios).
- **Scope**: Renderer only. No visual builder. SDUI + static UI coexist.

## Before You Start

1. Read `PROJECT_GOALS.md` for vision and constraints.
2. For implementation details: `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/SCHEMA-V1.md`.
3. Cursor rules in `.cursor/rules/` provide persistent context (project context, renderer patterns, EMR scheduler).

## Default Prompts / Instructions

When starting work:

- **Renderer work**: Follow patterns in `.cursor/rules/sdui-renderer.mdc`.
- **Scheduler work**: Follow `.cursor/rules/sdui-emr-scheduler.mdc`.
- **New components**: Register in component registry; support internal or external libs.
- **Schema changes**: Update `docs/SCHEMA-V1.md` and validator.

## Key Constraints

- No PHI in JSON
- No arbitrary JS
- No medical rules in JSON
- Logical layout preferred over absolute x-y
