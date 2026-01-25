# Feature Toggle POC (Databricks-Style)

Small, local, Docker-based POC that shows how to run the same code everywhere while flipping features via runtime configuration, similar to how Databricks Jobs use Widgets/Parameters.

## What this demonstrates
- Single main branch model: no env branches; promotions come from tags on one codebase.
- Single immutable artifact: one Docker image is built and reused for dev/QA/prod.
- Feature behavior is controlled only by runtime config (`FEATURES` env var).
- Same code runs in all environments; only feature flags change behavior.
- Simulated Databricks mapping:
  - `app/run.py` ~ notebook entrypoint triggered by a Job.
  - Env vars/`.env` files ~ Job parameters/Widgets.
  - `app/pipeline.py` ~ notebook orchestration.
  - `app/notebooks/*` ~ individual notebooks callable by flags.

## Repo layout (must match POC)
```
feature-toggle-poc/
|-- app/
|   |-- features.py        # feature identifiers
|   |-- pipeline.py        # orchestrates notebooks by feature flag
|   |-- run.py             # entrypoint (simulates Databricks Job)
|   `-- notebooks/         # notebook-like modules
|-- config/
|   |-- dev.env
|   |-- qa.env
|   `-- prod.env
|-- Dockerfile
|-- docker-compose.yml
`-- README.md
```

## Feature model
- Stable identifiers live in `app/features.py` and are not tied to branches or tags.
- Runtime flags come from a single env var: `FEATURES=feature_a,feature_b`.
- `app/pipeline.py` reads the flags at runtime and conditionally runs logic.
- Unknown flags are ignored so configs stay forward/backward compatible.

Current features:
- `data_quality_checks` - extra validation gate.
- `new_validation` - refactored validation notebook.
- `experimental_enrichment` - optional enrichment step.
- `notify_ops` - send notifications after publish.

## Environment behavior
- dev: all features enabled (`data_quality_checks,experimental_enrichment,notify_ops,new_validation`).
- qa: subset enabled (`data_quality_checks,experimental_enrichment,new_validation`).
- prod: production-approved only (`data_quality_checks,notify_ops`) - stays on legacy validation.

The same Docker image runs in every environment; only `FEATURES` differs.

## Docker / Compose
- Single `Dockerfile` builds a Python 3.11 image with the app code.
- `docker-compose.yml` defines three services (`dev`, `qa`, `prod`) that all use the same image but different `.env` files under `config/`.

## Run the demo locally
Prereq: Docker + docker compose.

```bash
# Build the single image and run all environments
docker compose up --build

# Or run one environment at a time
docker compose run --build dev
docker compose run --build qa
docker compose run --build prod
```

Expected behavior:
- Each service prints which features are enabled, which are disabled, and which flags are unknown (if any).
- The pipeline output changes only where feature-gated steps appear; base steps stay identical.
- Tagging the repo would select "what version runs", while `.env` files decide "which features are active" - no branching required.

## How this maps to a single-branch + tag promotion model
- Code lives on main; tags mark the artifact version (`feature-toggle-poc:tag`).
- The built image is immutable; dev/QA/prod pull the same tag.
- Promotion is changing the tag reference (what version) and/or the env file (which features) without changing code.
- Feature toggling replaces env-specific branches: configuration flips behavior at runtime.
