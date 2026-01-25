"""Core pipeline logic that reacts to runtime feature flags."""

from __future__ import annotations

from typing import Iterable, Tuple

from app import features


def _partition_features(
    requested: Iterable[str],
) -> Tuple[set[str], set[str], set[str]]:
    """Return (known_enabled, unknown, known_disabled)."""
    requested_set = set(requested)
    known_enabled = requested_set & features.ALL_FEATURES
    unknown = requested_set - features.ALL_FEATURES
    known_disabled = features.ALL_FEATURES - known_enabled
    return known_enabled, unknown, known_disabled


def run_pipeline(requested_features: Iterable[str]) -> None:
    """
    Simulate a Databricks-style job that toggles behavior purely via
    runtime feature flags (no code changes, no branch switching).
    """
    enabled, unknown, disabled = _partition_features(requested_features)

    print("=== Pipeline bootstrap ===")
    print(f"All supported features : {sorted(features.ALL_FEATURES)}")
    print(f"Enabled via runtime    : {sorted(enabled) if enabled else '[]'}")
    print(f"Disabled for this run  : {sorted(disabled) if disabled else '[]'}")
    if unknown:
        print(f"Ignoring unknown flags : {sorted(unknown)}")
    print()

    print("Step 1: Ingest base payload")
    print("Step 2: Transform core dataset")

    if features.FEATURE_DATA_QUALITY in enabled:
        print("Feature[data_quality_checks]: Running validation gate")
    else:
        print("Feature[data_quality_checks]: Skipped (flag off)")

    if features.FEATURE_ENRICHMENT in enabled:
        print("Feature[experimental_enrichment]: Applying enrichment logic")
    else:
        print("Feature[experimental_enrichment]: Skipped (flag off)")

    print("Step 3: Publish dataset")

    if features.FEATURE_NOTIFICATIONS in enabled:
        print("Feature[notify_ops]: Sending run notifications")
    else:
        print("Feature[notify_ops]: Skipped (flag off)")

    print("\nRun complete. Same image, different behavior via config.")
