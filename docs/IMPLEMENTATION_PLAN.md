# Industrial-Datagen: Fresh Start Plan

## Context

Rewrite the existing `indgen` Node.js/React industrial simulation platform as `industrial-datagen` using a modern, test-driven stack: Python FastAPI backend, React + TypeScript + PatternFly frontend, with Red Hat branding. The existing indgen is live at https://app-iesc.apps.cvn.osdu.opdev.io/ and serves as the feature reference. All 5 simulators must be ported. TDD/BDD is mandatory.

**Source reference:** `/home/mrhillsman/Development/misc/redhat-iesc/indgen`
**Target:** `/home/mrhillsman/Development/misc/redhat-iesc/industrial-datagen`

---

## Project Structure

```
industrial-datagen/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, CORS, lifespan
│   │   ├── config.py                # Settings (pydantic-settings)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py            # GET /api/health
│   │   │   ├── processes.py         # GET /api/processes, /api/processes/{type}/schema
│   │   │   ├── simulations.py       # POST start, GET current/history, PATCH params, POST stop/fault
│   │   │   ├── datasets.py          # POST generate, GET list/status/download, DELETE
│   │   │   ├── statistics.py        # GET /api/statistics/{processType}
│   │   │   └── streaming.py         # WebSocket + SSE endpoints
│   │   ├── simulators/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Abstract base simulator
│   │   │   ├── refinery.py          # Crude oil distillation
│   │   │   ├── chemical.py          # CSTR reactor
│   │   │   ├── pulp.py              # Kraft digester
│   │   │   ├── pharma.py            # GMP batch reactor
│   │   │   └── rotating.py          # Predictive maintenance
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── simulation.py        # Pydantic models for sim state/requests/responses
│   │   │   ├── dataset.py           # Dataset models
│   │   │   └── process.py           # Process schema models
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── base.py              # Abstract storage interface
│   │       ├── memory.py            # In-memory dict-based storage (default)
│   │       └── postgres.py          # Optional PostgreSQL/TimescaleDB backend
│   ├── tests/
│   │   ├── conftest.py              # Shared fixtures (FastAPI test client, simulators)
│   │   ├── unit/
│   │   │   ├── test_refinery.py
│   │   │   ├── test_chemical.py
│   │   │   ├── test_pulp.py
│   │   │   ├── test_pharma.py
│   │   │   └── test_rotating.py
│   │   ├── integration/
│   │   │   ├── test_api_health.py
│   │   │   ├── test_api_simulations.py
│   │   │   ├── test_api_datasets.py
│   │   │   └── test_api_streaming.py
│   │   └── features/                # BDD Gherkin feature files
│   │       ├── simulation.feature
│   │       ├── dataset_generation.feature
│   │       ├── anomaly_injection.feature
│   │       └── steps/               # pytest-bdd step definitions
│   │           ├── test_simulation_steps.py
│   │           ├── test_dataset_steps.py
│   │           └── test_anomaly_steps.py
│   ├── pyproject.toml               # Project metadata, deps, tool config
│   └── alembic/                     # DB migrations (optional persistence)
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── index.tsx
│   │   ├── App.tsx                  # PatternFly Page shell, routing
│   │   ├── components/
│   │   │   ├── ProcessSelector/     # Simulator type picker
│   │   │   ├── ParameterPanel/      # Sliders/inputs per simulator
│   │   │   ├── SimulationControls/  # Play/Pause/Reset/Download
│   │   │   ├── LiveChart/           # PatternFly Charts time-series
│   │   │   ├── StatisticsPanel/     # Summary metrics table
│   │   │   ├── DatasetManager/      # Generate/list/download datasets
│   │   │   ├── AnomalyPanel/        # Anomaly injection controls
│   │   │   └── ApiExplorer/         # Interactive API docs
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx        # Main simulation dashboard
│   │   │   └── Datasets.tsx         # Dataset management page
│   │   ├── hooks/
│   │   │   ├── useSimulation.ts     # Sim lifecycle + WebSocket
│   │   │   ├── useDataset.ts        # Dataset CRUD
│   │   │   └── useProcess.ts        # Process metadata
│   │   ├── services/
│   │   │   ├── api.ts               # Axios client (base URL, interceptors)
│   │   │   └── websocket.ts         # WebSocket client wrapper
│   │   ├── simulators/              # Client-side sim engines (standalone mode)
│   │   │   ├── base.ts
│   │   │   ├── refinery.ts
│   │   │   ├── chemical.ts
│   │   │   ├── pulp.ts
│   │   │   ├── pharma.ts
│   │   │   └── rotating.ts
│   │   └── types/
│   │       └── index.ts             # Shared TypeScript types
│   ├── tests/
│   │   ├── components/              # Vitest + React Testing Library
│   │   └── e2e/                     # Playwright BDD
│   │       ├── features/
│   │       │   ├── simulation.feature
│   │       │   └── dataset.feature
│   │       └── steps/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts               # Vite (not CRA)
├── deploy/
│   ├── Containerfile                # Multi-stage: build frontend + Python runtime
│   ├── docker-compose.yml           # Local dev (backend + frontend + optional postgres)
│   ├── openshift/
│   │   ├── Chart.yaml               # Helm chart
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── route.yaml
│   │       ├── configmap.yaml
│   │       └── pvc.yaml             # Optional persistence
│   └── bootc/
│       ├── Containerfile            # bootc image definition
│       ├── config/
│       │   ├── nginx/
│       │   └── systemd/
│       └── scripts/
│           ├── prepare-src.sh
│           ├── build.sh
│           └── convert-to-qcow2.sh
├── CLAUDE.md
├── README.md
└── Makefile                         # Dev commands: make test, make dev, make build
```

---

## Phased Implementation

### Phase 1: Project Scaffolding & Tooling

**Goal:** Runnable skeleton with test infrastructure — no features yet.

1. Initialize git repo
2. Create `backend/pyproject.toml` with dependencies:
   - Runtime: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `python-multipart`
   - Optional: `asyncpg`, `sqlalchemy[asyncio]`, `alembic`, `psycopg`
   - Test: `pytest`, `pytest-asyncio`, `pytest-bdd`, `pytest-cov`, `httpx`
   - Dev: `ruff`, `mypy`
3. Create `backend/app/main.py` — minimal FastAPI app with CORS + health endpoint
4. Create `frontend/` with Vite + React + TypeScript:
   - `npm create vite@latest` with react-ts template
   - Add PatternFly: `@patternfly/react-core`, `@patternfly/react-charts`, `@patternfly/react-icons`, `@patternfly/react-table`
   - Add: `axios`, `react-router-dom`
   - Test: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@playwright/test`
5. Create `Makefile` with targets: `dev-backend`, `dev-frontend`, `test-backend`, `test-frontend`, `test`, `lint`, `build`
6. Create `docker-compose.yml` for local dev
7. Write CLAUDE.md with project conventions
8. Verify: `make test` passes (trivial health check test)

### Phase 2: Backend Simulators (TDD)

**Goal:** All 5 simulators ported to Python with full test coverage.

**Test-first approach per simulator:**
1. Write `tests/features/simulation.feature` with Gherkin scenarios:
   - Scenario: Simulator produces valid output within expected ranges
   - Scenario: Parameter changes affect output
   - Scenario: Anomaly injection produces labeled anomalous data
   - Scenario: Catalyst/bearing degradation over time
   - Scenario: Dataset generation produces N samples with ~5% anomaly rate
2. Write unit tests (`tests/unit/test_<simulator>.py`) asserting:
   - `step()` returns all expected fields
   - Output values within physics-valid ranges
   - Parameter sensitivity (temperature up -> yield changes)
   - Anomaly labels are correct
3. Implement `simulators/base.py` — abstract base class:
   - `__init__(parameters)`, `step() -> dict`, `generate_dataset(samples, include_anomalies) -> list[dict]`
   - `get_schema() -> ProcessSchema` (parameter definitions + output fields)
4. Port each simulator from JS -> Python (reference: `indgen/backend-*-simulator.js`):
   - `refinery.py` — 16 output fields, distillation physics
   - `chemical.py` — 16 output fields, CSTR + Arrhenius kinetics
   - `pulp.py` — 24 output fields, Kraft H-factor model
   - `pharma.py` — 24 output fields, GMP compliance tracking
   - `rotating.py` — 18 output fields, vibration + fault injection
5. Verify: all BDD scenarios + unit tests pass

### Phase 3: Backend API Layer (TDD)

**Goal:** Full REST + WebSocket API matching indgen's 20+ endpoints.

**Test-first:**
1. Write `tests/features/dataset_generation.feature`:
   - Scenario: Generate dataset and download as CSV
   - Scenario: Generate dataset and download as JSON
   - Scenario: List datasets with pagination
2. Write integration tests per route module using `httpx.AsyncClient`
3. Implement storage layer:
   - `storage/base.py` — abstract interface (save_simulation, get_simulation, etc.)
   - `storage/memory.py` — dict-based implementation
4. Implement API routes:
   - `api/health.py` — server status, uptime, active sim count
   - `api/processes.py` — list simulators, get schema
   - `api/simulations.py` — full lifecycle (start/stop/current/history/parameters/fault)
   - `api/datasets.py` — generate/list/status/download/delete
   - `api/statistics.py` — computed stats per process type
   - `api/streaming.py` — WebSocket endpoint + SSE fallback
5. Wire up in `main.py` with APIRouter includes
6. Verify: all integration tests pass, OpenAPI docs at /docs

### Phase 4: Frontend Scaffolding with PatternFly

**Goal:** App shell with Red Hat branding, routing, PatternFly layout.

1. Set up PatternFly theming:
   - Import `@patternfly/react-core/dist/styles/base.css`
   - Configure Red Hat branding (logo, colors, favicon)
2. Create App shell:
   - `Page` with `Masthead` (Red Hat logo, app name)
   - `PageSidebar` with navigation (Dashboard, Datasets)
   - `PageSection` content areas
3. Set up React Router (Dashboard, Datasets pages)
4. Create API service layer (`services/api.ts`, `services/websocket.ts`)
5. Write component tests (RTL) for shell rendering
6. Verify: app renders with PatternFly styling, pages route correctly

### Phase 5: Frontend Features (TDD)

**Goal:** All UI features working with both standalone and API modes.

**Per component (test first with RTL):**
1. `ProcessSelector` — PatternFly `ToggleGroup` or `Select` for 5 simulators
2. `ParameterPanel` — `Slider` + `NumberInput` per simulator parameter
3. `SimulationControls` — `Button` group (Start/Stop/Reset), `Switch` for API/standalone mode
4. `LiveChart` — `@patternfly/react-charts` ChartLine/ChartArea for real-time data
5. `StatisticsPanel` — `Table` with current/min/max/avg stats
6. `DatasetManager` — generate form, `Table` listing, download buttons
7. `AnomalyPanel` — anomaly rate config, fault injection (rotating equipment)
8. Port client-side simulators to TypeScript (`frontend/src/simulators/`)
9. Custom hooks: `useSimulation` (WebSocket lifecycle), `useDataset`, `useProcess`
10. Verify: all component tests pass, features work in standalone mode

### Phase 6: Integration & E2E Tests

**Goal:** Full stack validated with Playwright BDD.

1. Write Playwright feature files:
   - Scenario: User selects refinery simulator and starts simulation
   - Scenario: User generates and downloads a dataset
   - Scenario: Real-time chart updates with simulation data
   - Scenario: User switches between standalone and API mode
2. Configure Playwright to start both backend + frontend
3. Run full E2E suite
4. Verify: all E2E scenarios pass

### Phase 7: Deployment

**Goal:** Production-ready containers, OpenShift Helm chart, bootc image.

1. `deploy/Containerfile` — multi-stage:
   - Stage 1: Node 20 — build frontend (`npm run build`)
   - Stage 2: Python 3.12 — install backend deps, copy frontend build, run uvicorn
2. Helm chart (`deploy/openshift/`):
   - `Deployment` with health/readiness probes on `/api/health`
   - `Service` (ClusterIP port 8000)
   - `Route` (edge TLS)
   - `ConfigMap` for env vars (storage backend, log level)
   - Optional `PVC` + PostgreSQL `StatefulSet`
3. bootc image (`deploy/bootc/`):
   - CentOS Stream 9 base
   - Python 3.12 + nginx
   - systemd units for backend + nginx
   - Prepare/build/convert scripts
4. Verify: `docker build`, `helm template`, bootc build all succeed

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Build tool | Vite | Faster than CRA, better DX, ESM-native |
| Language | TypeScript (frontend) | Type safety, better IDE support, modern approach |
| Charts | @patternfly/react-charts | Consistent with PatternFly design, Victory-based |
| Backend runner | uvicorn | ASGI, native WebSocket, production-grade |
| Testing BDD | pytest-bdd (back) + Playwright (front) | Gherkin feature files shared vocabulary |
| Storage abstraction | Strategy pattern | Swap in-memory <-> PostgreSQL via config |
| Simulator base | ABC with dataclass schemas | Consistent interface, self-documenting parameters |
| State management | React hooks + context | No Redux needed for this scale |

## Red Hat / PatternFly Branding

- Use PatternFly's built-in Red Hat font stack (RedHatDisplay, RedHatText)
- Color palette: `--pf-t--global--color--brand--default` (Red Hat red #EE0000 for accents)
- Masthead with Red Hat logo
- Dark theme via `pf-v6-theme-dark` class
- All components from @patternfly/react-core v6 (latest)

## Dependencies Summary

### Backend (pyproject.toml)
```
fastapi>=0.115
uvicorn[standard]>=0.34
pydantic>=2.10
pydantic-settings>=2.7
python-multipart>=0.0.18
# optional persistence
asyncpg>=0.30
sqlalchemy[asyncio]>=2.0
alembic>=1.14
# test
pytest>=8.3
pytest-asyncio>=0.25
pytest-bdd>=8.1
pytest-cov>=6.0
httpx>=0.28
# dev
ruff>=0.8
mypy>=1.13
```

### Frontend (package.json)
```
react, react-dom ^19
react-router-dom ^7
@patternfly/react-core ^6
@patternfly/react-charts ^8
@patternfly/react-icons ^6
@patternfly/react-table ^6
axios ^1.7
# dev
typescript ^5.7
vite ^6
vitest ^2
@testing-library/react ^16
@testing-library/jest-dom ^6
@playwright/test ^1.49
```

---

## Verification

After each phase:
1. `make test-backend` — pytest with coverage report
2. `make test-frontend` — vitest + RTL tests
3. `make lint` — ruff (Python) + eslint (TypeScript)
4. `make type-check` — mypy (Python) + tsc --noEmit (TypeScript)
5. Phase 6: `make test-e2e` — Playwright full stack
6. Phase 7: `make build` — Containerfile builds successfully
