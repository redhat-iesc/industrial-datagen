# Industrial-Datagen

Industrial process simulation platform for AI/ML dataset generation. Rewrite of `indgen` with modern, test-driven stack.

## Stack

- **Backend:** Python 3.12+, FastAPI, uvicorn, Pydantic
- **Frontend:** React 19, TypeScript, Vite, PatternFly v6
- **Testing:** pytest + pytest-bdd (backend), Vitest + RTL + Playwright (frontend)
- **Deployment:** Containerfile, OpenShift Helm chart, bootc

## Development

```bash
make dev-backend     # Start FastAPI dev server (port 8000)
make dev-frontend    # Start Vite dev server (port 5173)
make test            # Run all tests
make test-backend    # pytest with coverage
make test-frontend   # vitest
make test-e2e        # Playwright E2E
make lint            # ruff + eslint
make type-check      # mypy + tsc --noEmit
make build           # Container build
```

## Project Layout

```
backend/          Python FastAPI backend
  app/            Application code
    api/          Route handlers
    simulators/   5 physics-based simulator engines
    models/       Pydantic request/response models
    storage/      Pluggable storage (in-memory default, PostgreSQL optional)
  tests/          pytest unit, integration, and BDD tests
frontend/         React + TypeScript + PatternFly frontend
  src/
    components/   PatternFly UI components
    pages/        Route pages
    hooks/        Custom React hooks
    services/     API client + WebSocket
    simulators/   Client-side simulation engines (standalone mode)
  tests/          Vitest component tests + Playwright E2E
deploy/           Deployment configs
  openshift/      Helm chart
  bootc/          Immutable OS packaging
```

## Conventions

- **TDD/BDD required:** Write tests before implementation. BDD uses Gherkin `.feature` files.
- **Red Hat branding:** PatternFly v6, RedHatDisplay/RedHatText fonts, brand color palette.
- **Type safety:** TypeScript strict mode (frontend), Pydantic models + mypy (backend).
- **No CRA:** Use Vite for frontend build tooling.
- **Storage abstraction:** All data access goes through `storage/base.py` interface. Default is in-memory; PostgreSQL is opt-in via config.

## Simulators

Five physics-based industrial process simulators:
1. **Refinery** — crude oil distillation (16 output fields)
2. **Chemical** — CSTR continuous reactor (16 output fields)
3. **Pulp & Paper** — Kraft digester (24 output fields)
4. **Pharmaceutical** — GMP batch reactor (24 output fields)
5. **Rotating Equipment** — predictive maintenance with fault injection (18 output fields)

## Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) — phased build plan with architecture decisions
