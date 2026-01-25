"""Core pipeline logic that reacts to runtime feature flags."""

from __future__ import annotations

from typing import Iterable, Tuple

from app import feature_registry, features
from app.notebooks import base_steps
from app.utils import feature_policies


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
    requested_set = set(requested_features)
    enabled, policy_logs = feature_policies.apply_policies(requested_set)
    for log in policy_logs:
        print(log)
    for log in feature_registry.REGISTRY_LOGS:
        print(log)

    enabled, unknown, disabled = _partition_features(enabled)

    print("=== Pipeline bootstrap ===")
    print(f"All supported features : {sorted(features.ALL_FEATURES)}")
    print(f"Enabled via runtime    : {sorted(enabled) if enabled else '[]'}")
    print(f"Disabled for this run  : {sorted(disabled) if disabled else '[]'}")
    if unknown:
        print(f"Ignoring unknown flags : {sorted(unknown)}")
    print()

    base_steps.ingest()
    base_steps.transform()

    suppressed: set[str] = set()
    pre_entries = [e for e in feature_registry.FEATURE_REGISTRY if e.stage == "pre"]
    post_entries = [e for e in feature_registry.FEATURE_REGISTRY if e.stage == "post"]

    _execute_entries(pre_entries, enabled, suppressed)
    base_steps.publish()

    _execute_entries(post_entries, enabled, suppressed)

    print("\nRun complete. Same image, different behavior via config.")


def _execute_entries(
    entries: list[feature_registry.FeatureEntry],
    enabled: set[str],
    suppressed: set[str],
) -> None:
    """Run or skip feature entries based on runtime flags and overrides."""
    for entry in entries:
        if entry.feature in suppressed:
            print(f"{entry.label}: skipped (overridden)")
            continue

        if entry.feature in enabled:
            entry.handler()
            suppressed.update(entry.overrides)
        else:
            print(f"{entry.label}: skipped (flag off)")
