"""
Feature flag lifecycle helpers.

Idea: As flags age out, you can mark them as baseline (always on) or retired
so the pipeline auto-adjusts without editing pipeline.py.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Tuple

import yaml

DEFAULT_POLICY_FILE = Path(__file__).resolve().parents[2] / "config" / "policies.yaml"
POLICY_FILE_ENV = "POLICY_FILE"


@dataclass(frozen=True)
class PolicyConfig:
    baseline: Set[str]
    retired: Set[str]
    logs: List[str]


def apply_policies(enabled: Set[str]) -> Tuple[Set[str], List[str]]:
    """
    Apply lifecycle policies to the enabled flag set:
    - Add baseline features (idempotent)
    - Remove retired features
    Returns the adjusted set plus log messages describing changes.
    """
    policy = _load_policies()
    logs: List[str] = list(policy.logs)
    adjusted = set(enabled)

    retired_hit = adjusted & policy.retired
    if retired_hit:
        adjusted -= policy.retired
        logs.append(f"Policy: removed retired features {sorted(retired_hit)}")

    added_baseline = policy.baseline - adjusted
    if added_baseline:
        adjusted |= policy.baseline
        logs.append(f"Policy: auto-enabled baseline features {sorted(added_baseline)}")

    if not logs:
        logs.append("Policy: no lifecycle adjustments applied")

    return adjusted, logs


def _load_policies() -> PolicyConfig:
    """Load baseline/retired feature settings from a config file."""
    path = Path(os.getenv(POLICY_FILE_ENV, DEFAULT_POLICY_FILE))
    if not path.exists():
        return PolicyConfig(baseline=set(), retired=set(), logs=[f"Policy: {path} not found; no lifecycle adjustments applied"])

    try:
        with path.open() as fh:
            raw = yaml.safe_load(fh) or {}
    except Exception:
        return PolicyConfig(baseline=set(), retired=set(), logs=[f"Policy: could not parse {path}; no lifecycle adjustments applied"])

    baseline = set(raw.get("baseline_features", []))
    retired = set(raw.get("retired_features", []))
    return PolicyConfig(baseline=baseline, retired=retired, logs=[f"Policy: loaded {path}"])
