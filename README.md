# Getaround - Delay Analysis & Pricing API

[![CI](https://github.com/tryph0n/getaround-pricing-delay/actions/workflows/ci.yml/badge.svg)](https://github.com/tryph0n/getaround-pricing-delay/actions/workflows/ci.yml)

> End-to-end data science project for the Getaround car rental platform: a Streamlit dashboard to analyze checkout delays between rentals, and a FastAPI-served ML pricing prediction API, tracked with MLflow and containerized with Docker.

## Business Problem

Getaround is a car-sharing platform where owners rent their cars to drivers. When a car is returned late by one driver, it creates a cascade of problems for the next driver's rental -- delays, cancellations, and lost revenue. The product team needs data-driven answers to two key questions:

1. **Delay management**: What minimum time buffer should be enforced between consecutive rentals, and should it apply to all cars or only those with the "Connect" (keyless) feature?
2. **Pricing optimization**: Can we predict the optimal daily rental price for a car based on its features, helping owners maximize revenue?

This project delivers an interactive dashboard for delay analysis and an ML-powered API for pricing predictions.

## Learning objectives

This is a training course project. It covers three learning objectives:

| Learning objective | Implementation |
|--------------------|----------------|
| Standardize an ML environment with MLflow and Docker | MLflow experiment tracking (3 models compared), Docker multi-stage builds for HF Spaces deployment |
| Create an API for ML predictions at scale | FastAPI REST API with Pydantic validation, auto-generated documentation, deployed on Hugging Face Spaces |
| Deploy a web app with predictive statistics | Streamlit dashboard with interactive delay analysis, threshold simulation, and ML-powered pricing predictions |

## Project components

| Component | Link |
|-----------|------|
| Source, tests and CI (this repository) | https://github.com/tryph0n/getaround-pricing-delay |
| Pricing API demo (Swagger docs) | https://sam-bot-get-around-api.hf.space/docs |
| Delay analysis dashboard demo | https://sam-bot-get-around-dashboard.hf.space |
| API deployment repository (copy of the `make stage-api` tree) | https://github.com/tryph0n/getaround-pricing-api |
| Dashboard deployment repository (copy of the `make stage-dashboard` tree) | https://github.com/tryph0n/getaround-delay-dashboard |

Change the code here. The deployment repositories are copies of the staged trees.

## Key Results

Best pricing model: **GradientBoosting** (RMSE = 16.14, R² = 0.762)

- 3 models compared: Linear Regression, Random Forest, Gradient Boosting
- Dashboard enables Product Managers to simulate the revenue impact of setting a minimum delay threshold between consecutive rentals

### Model Comparison

| Model | RMSE | MAE | R-squared |
|-------|------|-----|---------|
| Linear Regression | 17.95 | 12.13 | 0.706 |
| Random Forest | 16.87 | 10.72 | 0.740 |
| Gradient Boosting | **16.14** | **10.53** | **0.762** |

Best model: **Gradient Boosting** (lowest RMSE, highest R-squared). Saved as `models/best_model.joblib`.

## Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.11 |
| API | FastAPI, Uvicorn, Pydantic |
| Dashboard | Streamlit, Plotly |
| ML | scikit-learn, MLflow |
| Data | pandas, NumPy |
| Testing | pytest |
| Linting | ruff |
| Package Manager | uv |
| Containerization | Docker |

## Prerequisites

- **Python** >=3.11, <3.12
- **uv** -- [installation guide](https://docs.astral.sh/uv/)
- **Docker** -- for building HF Spaces images (`deploy/hf-api/`, `deploy/hf-dashboard/`)
- **Make** -- for convenience commands

## Quick Start

```bash
git clone https://github.com/tryph0n/getaround-pricing-delay.git && cd getaround-pricing-delay
cp .env.example .env  # optional, defaults work out of the box
make install-dev      # Install all dependencies (dev and notebooks groups)
make train            # Train model (generates models/best_model.joblib)
make run-mlflow       # View training experiments at http://localhost:5000
make run-api          # Start API locally (port 8000)
make run-dashboard    # Start dashboard locally (port 8501, in another terminal)
```

For production/Docker builds, see `deploy/DEPLOYMENT.md`.

## Essential Commands

| Command | Description |
|---------|-------------|
| `make install-prod` | Install production dependencies |
| `make install-dev` | Install all dependencies (dev and notebooks groups) |
| `make train` | Train ML models with MLflow tracking |
| `make run-api` | Start FastAPI server |
| `make run-dashboard` | Start Streamlit dashboard |
| `make run-mlflow` | Start MLflow UI on port 5000 |
| `make lint` | Run ruff linter |
| `make format` | Format code with ruff |
| `make test` | Run tests |
| `make stage-api` | Build the API staging tree in `.tmp/hf-api/` (no upload) |
| `make stage-dashboard` | Build the dashboard staging tree in `.tmp/hf-dashboard/` (no upload) |
| `make deploy-all` | Deploy API and dashboard to HF Spaces, owner only (see [Deployment](deploy/DEPLOYMENT.md)) |
| `make clean` | Remove cache files |

## Tests

```bash
uv run pytest -q                                             # unit and integration tests
uv run pytest tests/unit --cov=src --cov-report=term-missing  # unit tests with coverage
```

The coverage threshold is 90% (`fail_under` in `pyproject.toml`). The integration
tests need a trained model (`make train`). Without the model they are skipped
locally. CI trains a model and fails if an integration test is skipped.

## Teardown

```bash
make clean            # Remove __pycache__, .pyc, .pytest_cache, .ruff_cache
```

`models/best_model.joblib` and `mlruns/` are gitignored artifacts generated by `make train`. To remove them manually:

```bash
rm -rf models/ mlruns/
```

These artifacts are not versioned. They are regenerated by `make train`.

## Data

Three files in `data/`:

| File | Used by |
|------|---------|
| `data/get_around_delay_analysis.xlsx` | Notebook 01 (delay analysis EDA), which reads it and writes the delay CSV |
| `data/get_around_delay_analysis.csv` | Dashboard (delay analysis) |
| `data/get_around_pricing_project.csv` | ML pipeline (pricing model training) |

Sources, as listed in `notebooks/00_assignment.ipynb`:
[delay analysis](https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx) and
[pricing](https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv).

Data provided by the Jedha training course (Getaround case study). The provider states no licence. The data files are not covered by the code licence.

Late-return rates depend on the base: 52.1% of all ended rentals, 57.5% of ended rentals with a recorded checkout delay. The dashboard uses the second, notebook 01 the first.

Trained model saved as `models/best_model.joblib` (gitignored).

## Documentation

- [Architecture](docs/ARCHITECTURE.md) -- System diagrams and data flow
- [Deployment](deploy/DEPLOYMENT.md) -- Step-by-step deployment guide for Hugging Face Spaces
- [Delay Analysis EDA](notebooks/01_delay_analysis_eda.ipynb) -- Exploratory analysis of checkout delays
- [Pricing ML EDA](notebooks/02_pricing_ml_eda.ipynb) -- Feature analysis and model selection

For production deployment to HF Spaces, see `deploy/DEPLOYMENT.md`.

## Possible Improvements

- **CI/CD pipeline**: Automate deployment via GitHub Actions instead of the current manual `make deploy-*` workflow.
- **Test coverage**: Add integration tests with a real database and increase unit test coverage for edge cases.
- **Model versioning**: Use MLflow Model Registry for formal model promotion (dev -> staging -> prod) instead of a single `best_model.joblib`.
- **Dashboard performance**: Cache expensive Plotly computations for large datasets to improve load times.
- **Monitoring**: Add API request logging and model prediction drift detection to catch degradation early.
- **Port configuration**: HF Spaces requires port 7860 (platform constraint). Local dev ports are configurable via `.env`. A unified port configuration across all environments would require a reverse proxy on HF.

## License

The code is released under the [MIT License](LICENSE). The data files are not
covered by it (see [Data](#data)).
