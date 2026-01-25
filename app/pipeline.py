"""Core pipeline logic that reacts to runtime feature flags."""

from __future__ import annotations

from typing import Iterable, Tuple

from app import features
from app.notebooks import (
    base_steps,
    enrichment,
    notifications,
    quality_legacy,
    quality_new,
)


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

    base_steps.ingest()
    base_steps.transform()

    if features.FEATURE_NEW_VALIDATION in enabled:
        quality_new.run()
    else:
        # keep the existing behavior, optionally still behind the old flag
        if features.FEATURE_DATA_QUALITY in enabled:
            quality_legacy.run()
        else:
            print("Notebook[quality]: skipped (flag off)")

    if features.FEATURE_ENRICHMENT in enabled:
        enrichment.run()
    else:
        print("Notebook[enrichment]: skipped (flag off)")

    base_steps.publish()

    if features.FEATURE_NOTIFICATIONS in enabled:
        notifications.run()
    else:
        print("Notebook[notifications]: skipped (flag off)")


    print("\nRun complete. Same image, different behavior via config.")
