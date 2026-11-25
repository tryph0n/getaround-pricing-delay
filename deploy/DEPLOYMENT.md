# Deployment Guide

Deploys are manual. Only the owner of the Hugging Face Spaces runs them: the
upload needs the owner's Hugging Face token. CI builds the Docker images
from the staged trees and tests them, but it never uploads anything.

## Prerequisites

- Python 3.11 with `uv` installed
- The `hf` command line tool, run through `uvx` at the version pinned in the
  Makefile (`HF_HUB_VERSION`, huggingface_hub 1.x). No other install is needed.
- Authenticated with the Hugging Face Hub:
  `uvx --from huggingface_hub==<HF_HUB_VERSION> hf auth login`
- For the API: a trained model at `models/best_model.joblib`

## Architecture

The project source of truth is the repository root. Deployment follows an
**assemble-on-deploy** strategy:

- `deploy/hf-api/` and `deploy/hf-dashboard/` hold the files of each Space:
  `Dockerfile`, `README.md`, `.dockerignore`, `.gitignore`, `.gitattributes`
  and a per-demo dependency list (`pyproject.toml`, `uv.lock`). Each list holds
  only what its demo needs. The root `pyproject.toml` and `uv.lock` are not
  deployed.
- `make stage-api` and `make stage-dashboard` assemble these files with the
  required source files in `.tmp/hf-api/` and `.tmp/hf-dashboard/`. They
  upload nothing.
- `make deploy-api` and `make deploy-dashboard` run the stage target, then
  upload the staged tree with `hf upload`. The upload does not delete files
  that are already in the Space.
- Hugging Face Spaces builds the Docker image from the uploaded `Dockerfile`.

The deployment repositories
[getaround_api](https://github.com/tryph0n/getaround_api) and
[getaround_dashboard](https://github.com/tryph0n/getaround_dashboard) are copies
of the staged trees. They are updated by hand from `.tmp/hf-*` after a deploy.
Change the code here, not there.

## Commands

```bash
make stage-api           # Build the API staging tree, no upload
make stage-dashboard     # Build the dashboard staging tree, no upload
make deploy-api          # Stage and upload the API (owner only)
make deploy-dashboard    # Stage and upload the dashboard (owner only)
make deploy-all          # Deploy both
```

Run `make -n deploy-api` or `make -n deploy-dashboard` first to read the exact
upload command.

## HF Spaces URLs

| Space | URL |
|-------|-----|
| API | https://sam-bot-get-around-api.hf.space |
| Dashboard | https://sam-bot-get-around-dashboard.hf.space |

## What Gets Deployed

The stage targets copy these files. The `COPY` lines of each `Dockerfile`
take the source, model and data from this list.

### API (`make stage-api`)

| Category | Files |
|----------|-------|
| Space files | the files of `deploy/hf-api/` that git does not ignore |
| License | `LICENSE` |
| Source | `src/__init__.py`, `src/api/`, `src/ml/__init__.py`, `src/ml/predict.py`, `src/ml/preprocessing.py`, `src/config/` |
| Model | `models/best_model.joblib` |

### Dashboard (`make stage-dashboard`)

| Category | Files |
|----------|-------|
| Space files | the files of `deploy/hf-dashboard/` that git does not ignore |
| License | `LICENSE` |
| Source | `src/__init__.py`, `src/dashboard/` (with `sections/`), `src/config/` |
| Data | `data/*.csv` |

Both stage targets remove `__pycache__` and `.ruff_cache` folders.

## Important Notes

- **Deploy the API before the dashboard.** The dashboard calls the API at
  runtime, so the API must be up and healthy first.
- **Port 7860 is mandatory.** HF Spaces Docker runtime expects the application
  to listen on port 7860. Both Dockerfiles are configured accordingly (FastAPI
  via `--port 7860`, Streamlit via `STREAMLIT_SERVER_PORT=7860`).
- **The staged model is the live model.** Do not stage a retrained model
  without a decision to replace the live one.
- HF Spaces rebuilds the Docker image on every upload. There is no incremental
  build cache between deploys.

## Environment Variables

- **Local development:** copy `.env.example` to `.env` and adjust values.
  Default ports are 8000 (API) and 8501 (dashboard).
- **HF Spaces production:** environment variables are baked into the
  Dockerfiles (`ENVIRONMENT=production`, `LOG_LEVEL=INFO`, `API_URL`, Streamlit
  settings). To override or add secrets (e.g., API keys), use the HF Space
  Settings > "Repository secrets" / "Variables" UI -- these are injected at
  runtime without rebuilding the image.

## Verification

After deploying, confirm the services are live:

```bash
curl https://sam-bot-get-around-api.hf.space/health
```

Then open the dashboard in a browser:

```
https://sam-bot-get-around-dashboard.hf.space
```
