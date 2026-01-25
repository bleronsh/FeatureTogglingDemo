"""Entrypoint that simulates a Databricks Job notebook."""

from __future__ import annotations

import os

from app import features, pipeline


def main() -> None:
    env_name = os.getenv("ENV_NAME", "local")
    raw_features = os.getenv("FEATURES", "")

    print("=== Databricks-style Job Simulation ===")
    print(f"Runtime environment : {env_name}")
    print("Job parameters      : environment variables (like Widgets/Params)")
    print(f"Raw FEATURES value  : {raw_features or '(empty)'}\n")

    enabled = features.parse_feature_flags(raw_features)
    pipeline.run_pipeline(enabled)


if __name__ == "__main__":
    main()
