.PHONY: dev-backend dev-frontend test test-backend test-frontend test-e2e lint type-check build clean

dev-backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && source .venv/bin/activate && pytest -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && npx vitest run

test-e2e:
	cd frontend && npx playwright test

lint:
	cd backend && source .venv/bin/activate && ruff check app/ tests/
	cd frontend && npx tsc --noEmit

type-check:
	cd backend && source .venv/bin/activate && mypy app/
	cd frontend && npx tsc --noEmit

build:
	podman build -f deploy/Containerfile -t industrial-datagen:latest .

clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.pytest_cache backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.vite
