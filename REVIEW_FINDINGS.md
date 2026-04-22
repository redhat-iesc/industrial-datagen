# Industrial Datagen - Issues & Recommendations

Auto-generated from project review on 2026-04-22. Organized by priority for incremental work.

---

## 🔴 High Priority

### H1: Dataset generation lacks temporal correlation

**Location:** `backend/app/simulators/base.py` - `BaseSimulator.generate_dataset()`

**Problem:** A new simulator instance is created per sample in `generate_dataset()`, so each row is an independent snapshot with no temporal continuity between steps. This defeats the purpose of time-series data for ML training (no autocorrelation, no drift patterns, no fault progression).

**Current code:**
```python
for i in range(samples):
    sim = self.__class__()  # fresh instance each iteration
    ...
    row = sim.step()
```

**Recommendation:** Refactor to step through a single instance across all samples, accumulating correlated data. Offer a separate "static snapshot" method for the current per-sample behavior.
```python
# New approach
async def generate_dataset(self, samples: int, include_anomalies: bool = True) -> list[dict]:
    dataset = []
    sim = self.__class__()
    for i in range(samples):
        is_anomaly = include_anomalies and random.random() < self._anomaly_rate()
        params = self._anomaly_params(i) if is_anomaly else self._normal_params(i)
        sim.parameters.update(params)
        sim.state["timeStep"] = i
        row = sim.step()
        row["anomaly"] = 1 if is_anomaly else 0
        dataset.append(row)
    return dataset
```

---

### H2: Global app state with mutable direct assignment

**Location:** `backend/app/main.py` — `lifespan()`, `backend/tests/conftest.py` — `client` fixture

**Problem:** Storage, simulation dicts, and tasks are directly assigned to `app.state`. This pattern:
- Bypasses any initialization protocol or validation
- Creates race conditions with multi-worker uvicorn deployments
- Makes testing fragile (tests mutate shared app state)
- No cleanup if a request crashes mid-operation

**Recommendation:** Introduce a proper dependency-injected `AppContext` class:
```python
class AppContext:
    storage: BaseStorage
    active_simulations: dict[str, BaseSimulator]
    simulation_tasks: dict[str, asyncio.Task[None]]
    rtsp_manager: RTSPStreamManager

    async def init(self): ...
    async def cleanup(self): ...

def get_app_context(request: Request) -> AppContext: ...
```
Use `Depends(get_app_context)` in route handlers instead of direct `app.state` access.

---

## H2 Work Plan

### Scope

| # | File | Change |
|---|--|------|
| 1 | `backend/app/context.py` | **NEW** — `AppContext` class with `init()`, `cleanup()` |
| 2 | `tests/unit/test_context.py` | **NEW** — unit tests for AppContext |
| 3 | `backend/app/main.py` | lifespan() injects AppContext; dependency |
| 4 | `backend/app/api/datasets.py` | Replace `_get_storage()` with context dep |
| 5 | `backend/app/api/simulations.py` | Replace `_get_storage/active_sims/sim_tasks` with context dep |
| 6 | `backend/app/api/streaming.py` | Replace `request.app.state` access with context dep |
| 7 | `backend/app/api/rtsp.py` | Replace `_get_manager()` with context dep |
| 8 | `tests/conftest.py` | Isolate test fixture with fresh AppContext |

### Commit Plan

#### Commit 1: Create AppContext class
- **What:** `AppContext(storage, sims, tasks, rtsp_manager)` with `async def cleanup()`
- **Tests:** `test_context.py` — init, cleanup, property access
- **Gate:** new + existing tests pass

#### Commit 2: Rewrite main.py lifespan + dependency
- **What:** lifespan creates `AppContext`; add `get_app_context` dep
- **Tests:** existing integration tests exercise the same endpoints
- **Gate:** `make test-backend` passes (no regression)

#### Commit 3: Update all route handlers
- **What:** datasets.py, simulations.py, streaming.py, rtsp.py — replace `request.app.state.*` with `Depends(get_app_context)`
- **Tests:** integration test coverage unchanged
- **Gate:** `make test-backend` passes

#### Commit 4: Update test fixture
- **What:** conftest creates fresh `AppContext` per test instead of mutating `app.state`
- **Tests:** re-run full suite
- **Gate:** all 169+ tests pass

### Risk Analysis

| Risk | Mitigation |
|------|------------|
| Streaming WebSocket/SSE needs context at accept/async context | Use `Depends` inside async endpoint body (works in FastAPI) |
| `_run_simulation()` background task needs access to storage/sims | Pass `AppContext` as arg to `_run_simulation()` |
| Existing test mocks for `app.state` break | Replace with fresh `AppContext` in conftest |

### Time Estimate: ~60 min

---

### H3: Streaming uses polling instead of push-based channel

**Location:** `backend/app/api/streaming.py` - both `simulation_websocket()` and `simulation_sse()`

**Problem:** Both transports poll `get_simulation_latest()` every 0.5s. This means:
- Clients with different poll states see inconsistent data
- Multiple clients each maintain separate polling loops (wasteful)
- No backpressure handling - a fast-producing client overwhelms slow consumers
- The SSE consumer and the simulation task race on storage reads

**Recommendation:** Use `asyncio.Queue` as a push channel:
```python
# In _run_simulation():
await event_queue.put(row)

# In SSE/WebSocket consumers:
while True:
    row = await event_queue.get()
    yield f"data: {json.dumps(row)}\n\n"
```
This eliminates polling gaps, race conditions, and makes consumers truly push-based.

---

## 🟡 Medium Priority

### M4: No error handling for storage write failures

**Location:** `backend/app/api/simulations.py` - `_run_simulation()`

**Problem:** Storage operations are called without try/except. Any transient I/O failure (disk full, DB disconnect in PostgreSQLStorage) silently crashes the simulation task. The task only catches `CancelledError`.

**Fix:** Wrap storage writes with retry logic and error reporting:
```python
try:
    await storage.append_simulation_data(sim_id, row)
except Exception as exc:
    logger.error("Storage write failed: %s", exc)
    # Optionally pause, retry, or signal failure to the client
```

---

### M5: Dataset rows stored as `dict[str, object]` - no schema validation

**Location:** `backend/app/storage/base.py`, `backend/app/storage/memory.py`

**Problem:** The storage layer uses `dict[str, object]` everywhere. There's no validation that stored rows match the simulator's output field schema. Corrupt or unexpected keys silently propagate through the system.

**Fix:** Introduce row validation in storage methods:
- Add `output_fields()` validation when saving rows
- Add Pydantic-based `SimulationDataRow` model for type-checking
- At minimum, document the expected schema in `BaseStorage` docstrings

---

### M6: Frontend `useSimulation` hook renders new simulators during state init

**Location:** `frontend/src/hooks/useSimulation.ts` - lines ~12-13

**Problem:**
```typescript
const [simulator, setSimulator] = useState<BaseSimulator>(() => createSimulator(selectedProcess));
const [parameters, setParameters] = useState<Record<string, number>>(() => ({ ...createSimulator(selectedProcess).parameters }));
```
When `selectedProcess` changes, `useState` initialization runs again, creating a second simulator instance. This causes stale references and unnecessary allocations.

**Fix:** Use a single `useRef`-backed simulator with explicit process-change effects:
```typescript
const simRef = useRef(createSimulator('refinery'));

useEffect(() => {
  simRef.current = createSimulator(selectedProcess);
  setData([]);
}, [selectedProcess]);
```

---

### M7: CORS allows `["*"]` with `allow_credentials=True` (semantically incorrect)

**Location:** `backend/app/main.py` - CORS middleware setup

**Problem:** Setting both `allow_origins=["*"]` and `allow_credentials=True` is semantically wrong. When credentials are enabled, browsers reject `"*"` as a wildcard origin. FastAPI will coerce this to `["*"]` without credentials anyway, but the config is misleading.

**Fix:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,  # match allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Or better: require explicit origin configuration in production.

---

### M8: No parameter range validation in the StartSimulationRequest

**Location:** `backend/app/models/simulation.py` - `StartSimulationRequest.parameters`

**Problem:** Parameters are accepted as bare `dict[str, float]` with no validation against the simulator's `ParameterDef` min/max ranges. A user can pass `temperature: 999` and get meaningless output without any warning.

**Fix:** Validate parameters against simulator schema at request time:
```python
@validator("parameters", pre=True)
def validate_parameters(cls, v, values):
    process_type = values.get("process_type")
    sim_cls = get_simulator_class(process_type)
    if sim_cls:
        defs = {p.name: (p.min_val, p.max_val) for p in sim_cls().parameter_defs()}
        for name, value in v.items():
            if name in defs:
                lo, hi = defs[name]
                if not (lo <= value <= hi):
                    raise ValueError(f"{name} must be between {lo} and {hi}")
    return v
```

---

### M9: TypeScript simulators diverge subtly from Python simulators

**Location:** `frontend/src/simulators/` vs `backend/app/simulators/`

**Problem:** The frontend and Python simulators are meant to be mirror implementations, but they use:
- Different noise implementations (percentage-based in TypeScript, absolute in Python)
- Different rounding precision (some fields differ)
- Different defaults (e.g., `p["temperature"]` vs `p["temp"]` naming in older versions)
- No regression test ensures they produce the same output for the same input

**Fix:** Add a cross-language test:
1. Export test fixtures (params + expected outputs) to `tests/fixtures/`
2. Run both Python and TypeScript simulators against the same fixture
3. Assert numerical equality within a tolerance (e.g., `atol=0.01`)

---

## 🟢 Low Priority

### L10: `make lint` runs `tsc --noEmit` but that's type-checking, not linting

**Location:** `Makefile` - `lint` target

**Problem:** `lint` runs `uv run ruff check app/ tests/` then `pnpm exec tsc --noEmit`. Then `type-check` does the same `tsc --noEmit` again. The type check is duplicated and semantically belongs in `type-check`, not `lint`.

**Fix:**
```makefile
lint:
	cd backend && uv run ruff check app/ tests/
	cd frontend && pnpm exec eslint .

type-check:
	cd backend && uv run mypy app/
	cd frontend && pnpm exec tsc --noEmit
```

---

### L11: Large image files committed to repo root

**Location:** `chemical-reactor.png` (62KB), `chemical-scrolled.png` (48KB)

**Problem:** Large screenshots at the repo root clutter the working directory. They're used in README.md but should live in `docs/`.

**Fix:** Move to `docs/screenshots/` and update `README.md` references to `docs/screenshots/`.

---

### L12: `POST /api/datasets/generate` blocks the HTTP worker thread

**Location:** `backend/app/api/datasets.py` - `generate_dataset()`

**Problem:** For `samples=100000`, the synchronous loop blocks the FastAPI worker entirely. No streaming response, no progress updates, no timeout protection.

**Fix:** Two options:
1. **Async task:** Return immediately, run generation in background, poll `/api/datasets/{id}/status`
2. **Streaming response:** `StreamingResponse` that yields partial output as it's generated

---

### L13: RTSP ffmpeg subprocesses have no resource limits or watchdog

**Location:** `backend/app/rtsp/manager.py`

**Problem:** Spawned ffmpeg processes have no:
- CPU/memory limits (could consume all host resources)
- Exit monitoring (hung ffmpeg leaves orphan processes)
- Timeout on connection failure

**Fix:** Add resource limits and a watchdog:
```python
process = await asyncio.create_subprocess_exec(
    "ffmpeg", ...,
    limit_bytes=1_000_000_000,  # limit output
)
# Monitor stderr for errors, kill on timeout
```

---

### L14: No pagination on `GET /api/simulations`

**Location:** `backend/app/api/simulations.py` - `list_simulations()`

**Problem:** Long-running deployments accumulate simulations indefinitely. Returning all at once is unbounded and can cause memory/issues.

**Fix:** Add query parameters:
```python
@router.get("/simulations")
async def list_simulations(
    limit: int = 50, offset: int = 0, ...
):
    sims = await storage.list_simulations(offset=offset, limit=limit)
    total = await storage.count_simulations()
    return {"data": sims, "total": total}
```
