# Implementation priorities

Journey Management is the core domain and therefore takes priority in the implementation order. User Management comes before AI Assistance since AI Assistance is the most expensive context (LLM dependency, cross-context event coordination) and gains most from the domain patterns being proven first.

**Deliberately deferred:** Daily Brief and Audio Guide are advanced automation features we will most likely not cover in this course.

## Implementation strategy

For every phase we will:

- Create necessary aggregate roots and invariants in the domain layer
- Create necessary repositories in the infrastructure layer
- Implement application services (command/query handlers)
- Wire up the FastAPI endpoints
- add the gained functionality to the frontend views

### Test driven development

For every new feature or domain concept, we will:

- Write failing tests that define the expected behavior
- Implement the minimum code necessary to pass the tests
- Refactor the code while keeping the tests green

# Repository structure

This repository will be organized to reflect the bounded context and layered architecture, with separate directories for each context and its corresponding domain, application, and infrastructure layers.

Inside `backend/src` — each bounded context is one package under the `sqr` namespace:

```text
.
├── dev                          # ./dev command interface — contract defined in CI-CD-PLAN.md §4
├── compose.yaml                 # multi-service environment (backend, frontend, db, cache) for dev + Stage 2 E2E
├── backend/                     # the Python 3.13 project — also the container boundary (bind-mounted as /app)
│   ├── pyproject.toml           # backend package: deps, ruff + pytest/coverage config
│   ├── uv.lock                  # exact dependency resolution (`uv sync --locked` installs exactly this)
│   ├── Dockerfile               # deps stage (uv sync into /opt/venv) + dev target (source arrives via bind-mount); Stage 3: release image also builds frontend as static assets
│   ├── src/sqr/                 # backend source, one package per bounded context
│   └── tests/                   # mirrors src/, one subtree per context (TDD per implementation strategy)
├── frontend/                    # own toolchain; views grouped per context to mirror the backend
├── .env.example                 # template for compose env vars (e.g. LLM API key once ai_assistance starts)
├── .pre-commit-config.yaml      # optional local ruff hook (CI-CD-PLAN.md §6)
├── .github/workflows/           # lint.yml (Stage 1), test.yml (Stage 2), release.yml (Stage 3)
├── docs/
│   ├── adr/                     # architecture decision records (rationale per significant choice)
│   └── uml/                     # UML module: context map, aggregate class diagrams
├── e2e/                         # Stage 2 E2E: collected separately, only runs against the compose environment
└── ...
```

Each context will have the same four-layer structure:
| layer | description |
|-------|-------------|
| domain | pure domain model (enforces invariants and business rules) |
| application | orchestrates use cases, defines commands, queries, and ports |
| infrastructure | implements the domain's ports, handles persistence and external services |
| interfaces | exposes the context via HTTP, CLI, or other adapters |

Journey Management as an example context:

```text
backend/src/sqr/journey_management/
├── domain/                      # pure model — no FastAPI/DB/framework imports
│   ├── journey/                 # aggregate cluster, vocabulary 1:1 from tmp/classdiagram.mermaid
│   │   ├── journey.py           # Journey aggregate root: title, start/end dates, addDestination(), updatePlan(), shareJourney()
│   │   ├── destination.py       # Destination entity (composition part of Journey): name, country, sequence
│   │   ├── activity.py          # Activity entity (composition part of Destination): times, location, markAsVisited(), reschedule()
│   │   ├── journey_companion.py # JourneyCompanion entity: role + permission, represents a User (sharing)
│   │   └── events.py            # JourneyCreated, DestinationAdded, ActivityRescheduled, ...
│   ├── repositories.py          # repository ports (interfaces) — implementations live in infrastructure
│   ├── services.py              # pure domain services spanning multiple aggregates
│   └── exceptions.py            # invariant violations, domain errors
├── application/
│   ├── commands/                # write side: one file per handler + input model
│   │   ├── create_journey.py
│   │   └── add_destination_to_journey.py
│   ├── queries/                 # read side: handlers returning DTOs
│   │   ├── get_journey.py
│   │   └── list_journeys.py
│   └── ports.py                 # what the app layer needs: unit of work, event bus, clock
├── infrastructure/
│   ├── persistence/
│   │   ├── in_memory/journey_repository.py   # fast fake for tests, first runnable version
│   │   └── sqlite/journey_repository.py      # real adapter + row mapper + migrations
│   └── events/                  # event publishing for cross-context coordination (needed by ai_assistance)
└── interfaces/
    └── http/
        ├── journeys.py          # FastAPI routers for this context
        └── schemas.py           # Pydantic request/response models — no domain objects leak out
```
