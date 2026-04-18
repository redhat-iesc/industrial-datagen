.PHONY: dev-backend dev-frontend test test-backend test-frontend test-e2e lint type-check build clean

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && pnpm run dev

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && pnpm exec vitest run

test-e2e:
	cd frontend && pnpm exec playwright test

lint:
	cd backend && uv run ruff check app/ tests/
	cd frontend && pnpm exec tsc --noEmit

type-check:
	cd backend && uv run mypy app/
	cd frontend && pnpm exec tsc --noEmit

build:
	podman build -f deploy/Containerfile -t industrial-datagen:latest .

clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.pytest_cache backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.vite
