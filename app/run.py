"""Entrypoint that simulates a Databricks Job notebook."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from app import features, pipeline


def main() -> None:
    config_path = os.getenv("CONFIG_FILE", "config/dev.yaml")
    env_name = os.getenv("ENV_NAME")
    raw_features = os.getenv("FEATURES", "")

    config_features, config_env_name, config_log = _load_env_config(config_path)
    if not env_name:
        env_name = config_env_name or "local"

    print("=== Databricks-style Job Simulation ===")
    print(f"Runtime environment : {env_name}")
    print("Job parameters      : YAML configs + environment overrides (like Widgets/Params)")
    print(f"Config file         : {config_log}")
    print(f"Raw FEATURES value  : {raw_features or '(empty)'}")

    if raw_features.strip():
        requested = features.parse_feature_flags(raw_features)
        print(f"Feature source      : FEATURES env -> {sorted(requested)}\n")
    else:
        requested = set(config_features)
        print(f"Feature source      : {config_path} -> {config_features or '[]'}\n")

    pipeline.run_pipeline(requested)


def _load_env_config(path_str: str) -> tuple[list[str], str | None, str]:
    path = Path(path_str)
    if not path.exists():
        return [], None, f"{path} (not found)"

    try:
        with path.open() as fh:
            raw = yaml.safe_load(fh) or {}
    except Exception:
        return [], None, f"{path} (parse error)"

    features_list = raw.get("features", []) or []
    env_name = raw.get("env_name")
    return features_list, env_name, f"{path}"


if __name__ == "__main__":
    main()
