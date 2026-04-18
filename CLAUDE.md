# Industrial-Datagen

Industrial process simulation platform for AI/ML dataset generation. Rewrite of `indgen` with modern, test-driven stack.

## Stack

- **Backend:** Python 3.12+, FastAPI, uvicorn, Pydantic, uv
- **Frontend:** React 19, TypeScript, Vite, PatternFly v6, pnpm
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

## Git

- **Conventional Commits:** All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) spec (`feat:`, `fix:`, `test:`, `chore:`, `docs:`, `refactor:`, `ci:`, etc.).
- **Incremental commits:** Make small, logical commits — one concern per commit. Do not batch unrelated changes.
- **Tests required:** All tests must pass before committing. Run `make test-frontend` / `make test-backend` to verify.
- **No force-push to main:** Never force-push to the main branch.

## Simulators

Five physics-based industrial process simulators (see [docs/SIMULATORS.md](docs/SIMULATORS.md) for full parameter/output specs):
1. **Refinery** — crude oil distillation (4 params, 17 outputs)
2. **Chemical** — CSTR continuous reactor (6 params, 17 outputs)
3. **Pulp & Paper** — Kraft digester (6 params, 25 outputs)
4. **Pharmaceutical** — GMP batch reactor (7 params, 26 outputs)
5. **Rotating Equipment** — predictive maintenance with fault injection (6 params, 20 outputs)

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — system design, data flow, project structure (with mermaid diagrams)
- [API Reference](docs/API_REFERENCE.md) — all REST, WebSocket, and SSE endpoints
- [Simulators](docs/SIMULATORS.md) — physics models, parameters, output fields
- [Data Model](docs/DATA_MODEL.md) — TypeScript/Pydantic types, storage contract
- [Development](docs/DEVELOPMENT.md) — setup, testing, code conventions, dependency list
- [Deployment](docs/DEPLOYMENT.md) — container builds, Docker Compose, OpenShift, bootc
- [Diagrams](docs/diagrams/) — standalone `.mermaid` source files for all architecture diagrams
