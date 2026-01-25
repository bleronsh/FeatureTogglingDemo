# Feature Toggle POC (Databricks-Style)

Small, local, Docker-based POC that shows how to run the same code everywhere while flipping features via runtime configuration, similar to how Databricks Jobs use Widgets/Parameters.

## What this demonstrates
- Single main branch model: no env branches; promotions come from tags on one codebase.
- Single immutable artifact: one Docker image is built and reused for dev/QA/prod.
- Feature behavior is controlled only by runtime config (YAML-configured flags).
- Same code runs in all environments; only feature flags change behavior.
- Simulated Databricks mapping:
  - `app/run.py` ~ notebook entrypoint triggered by a Job.
  - YAML configs + env overrides ~ Job parameters/Widgets.
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
|   |-- dev.yaml           # env config (env_name, features list)
|   |-- qa.yaml
|   |-- prod.yaml
|   |-- features.yaml      # feature->notebook mapping (registry)
|   `-- policies.yaml      # baseline/retired flags
|-- Dockerfile
|-- docker-compose.yml
`-- README.md
```

## Feature model
- Stable identifiers live in `app/features.py` and are not tied to branches or tags.
- Runtime flags come from YAML config (`config/*.yaml`) and can be overridden by a `FEATURES` env var if desired.
- `app/pipeline.py` reads the flags at runtime and conditionally runs logic (registry-driven).
- Unknown flags are ignored so configs stay forward/backward compatible.

Current features:
- `data_quality_checks` - extra validation gate.
- `experimental_enrichment` - enrichment notebook (baseline via policy).
- `new_validation` - refactored validation notebook.
- `notify_ops` - send notifications after publish.

Lifecycle helper:
- `app/utils/feature_policies.py` + `config/policies.yaml` let you auto-baseline or retire flags without touching `pipeline.py`; invoked on every run and logs what it does.
- `config/features.yaml` maps feature IDs to notebook modules/handlers; edit this file (not code) to register new notebooks. Pipeline auto-loads it and logs the source.

## Add a new notebook-driven feature (no code edits)
1) Create a notebook module under `app/notebooks/` with a callable (default `run`).
2) Add an entry to `config/features.yaml`, e.g.:
   ```yaml
   - id: my_new_feature
     module: app.notebooks.my_new_feature
     callable: run
     label: Notebook[my_new_feature]
     stage: pre
     overrides: []
   ```
3) Turn it on per environment by listing it in the env YAML (e.g., `config/dev.yaml`), or baseline it via `config/policies.yaml` if you want it always on. You can still override with `FEATURES` env if you prefer.

## Environment behavior
- dev (`config/dev.yaml`): validation flags plus notifications (`data_quality_checks,notify_ops,new_validation,my_newer_feature,my_new_feature`).
- qa (`config/qa.yaml`): validation only (`data_quality_checks`) - stays on legacy validation until promoted.
- prod (`config/prod.yaml`): production-approved only (`data_quality_checks,notify_ops`) - stays on legacy validation.

Promotion demo (toggle-only, no code edits):
- Dev already runs the new validation via `new_validation`.
- To promote to QA, add `new_validation` to `features` in `config/qa.yaml`.
- To promote to Prod, add `new_validation` to `features` in `config/prod.yaml`.

The same Docker image runs in every environment; only YAML configuration differs (or a `FEATURES` override if you set one).

## Docker / Compose
- Single `Dockerfile` builds a Python 3.11 image with the app code.
- `docker-compose.yml` defines three services (`dev`, `qa`, `prod`) that all use the same image but point to different YAML env configs (`CONFIG_FILE=/app/config/<env>.yaml`).

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
- Tagging the repo would select "what version runs", while YAML config decides "which features are active" - no branching required.

## How this maps to a single-branch + tag promotion model
- Code lives on main; tags mark the artifact version (`feature-toggle-poc:tag`).
- The built image is immutable; dev/QA/prod pull the same tag.
- Promotion is changing the tag reference (what version) and/or the env file (which features) without changing code.
- Feature toggling replaces env-specific branches: configuration flips behavior at runtime.
