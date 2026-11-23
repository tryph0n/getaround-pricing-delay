-include .env

API_HOST ?= 0.0.0.0
API_PORT ?= 8000
DASHBOARD_PORT ?= 8501
HF_HUB_VERSION := 1.33.0

.PHONY: install-prod install-dev lint format test train run-api run-dashboard run-mlflow clean help check-model stage-api stage-dashboard deploy-api deploy-dashboard deploy-all

help:
	@echo "Available commands:"
	@echo "  make install-prod  - Install production dependencies"
	@echo "  make install-dev   - Install all dependencies (dev and notebooks)"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with ruff"
	@echo "  make test          - Run tests"
	@echo "  make train         - Train ML models with MLflow tracking"
	@echo "  make run-api       - Start FastAPI server"
	@echo "  make run-dashboard - Start Streamlit dashboard"
	@echo "  make run-mlflow    - Start MLflow UI"
	@echo "  make stage-api        - Build the API staging tree in .tmp/hf-api"
	@echo "  make stage-dashboard  - Build the dashboard staging tree in .tmp/hf-dashboard"
	@echo "  make deploy-api       - Stage and upload the API to HF Spaces (owner only)"
	@echo "  make deploy-dashboard - Stage and upload the dashboard to HF Spaces (owner only)"
	@echo "  make deploy-all       - Deploy both API and dashboard to HF Spaces"
	@echo "  make clean         - Remove cache files"

install-prod:
	uv sync --no-group dev

install-dev:
	uv sync --all-groups

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

train: ## Train ML models with MLflow tracking
	uv run python -m src.ml.train

run-api:
	PYTHONPATH=. uv run uvicorn src.api.main:app --reload --host $(API_HOST) --port $(API_PORT)

run-dashboard:
	PYTHONPATH=. uv run streamlit run src/dashboard/app.py --server.port $(DASHBOARD_PORT)

run-mlflow: ## Start MLflow UI
	uv run mlflow ui --backend-store-uri ./mlruns --port 5000

check-model:
	@test -f models/best_model.joblib || (echo "ERROR: models/best_model.joblib not found. Run 'make train' first." && exit 1)

stage-api: check-model
	rm -rf .tmp/hf-api
	mkdir -p .tmp/hf-api/src/ml .tmp/hf-api/models
	(cd deploy/hf-api && git ls-files -z --cached --others --exclude-standard | tar --null -T - -cf -) | tar -C .tmp/hf-api -xf -
	cp LICENSE .tmp/hf-api/
	cp src/__init__.py .tmp/hf-api/src/
	cp -r src/api .tmp/hf-api/src/
	cp src/ml/__init__.py src/ml/predict.py src/ml/preprocessing.py .tmp/hf-api/src/ml/
	cp -r src/config .tmp/hf-api/src/
	cp models/best_model.joblib .tmp/hf-api/models/
	find .tmp/hf-api \( -name "__pycache__" -o -name ".ruff_cache" \) -prune -exec rm -rf {} + 2>/dev/null || true

stage-dashboard:
	rm -rf .tmp/hf-dashboard
	mkdir -p .tmp/hf-dashboard/src .tmp/hf-dashboard/data
	(cd deploy/hf-dashboard && git ls-files -z --cached --others --exclude-standard | tar --null -T - -cf -) | tar -C .tmp/hf-dashboard -xf -
	cp LICENSE .tmp/hf-dashboard/
	cp src/__init__.py .tmp/hf-dashboard/src/
	cp -r src/dashboard .tmp/hf-dashboard/src/
	cp -r src/config .tmp/hf-dashboard/src/
	cp data/*.csv .tmp/hf-dashboard/data/
	find .tmp/hf-dashboard \( -name "__pycache__" -o -name ".ruff_cache" \) -prune -exec rm -rf {} + 2>/dev/null || true

deploy-api: stage-api
	uvx --from huggingface_hub==$(HF_HUB_VERSION) hf upload sam-bot/get-around-api .tmp/hf-api . --repo-type space --commit-message "Deploy API"

deploy-dashboard: stage-dashboard
	uvx --from huggingface_hub==$(HF_HUB_VERSION) hf upload sam-bot/get-around-dashboard .tmp/hf-dashboard . --repo-type space --commit-message "Deploy dashboard"

deploy-all: deploy-api deploy-dashboard

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
