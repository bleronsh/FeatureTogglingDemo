"""Helpers for loading feature registry configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

DEFAULT_FEATURE_CONFIG = Path(__file__).resolve().parents[1] / "config" / "features.json"
FEATURE_CONFIG_ENV = "FEATURE_CONFIG_FILE"


@dataclass(frozen=True)
class FeatureConfigEntry:
    feature_id: str
    module: str
    callable_name: str = "run"
    label: str | None = None
    stage: str = "pre"
    overrides: List[str] = field(default_factory=list)


def load_feature_config() -> Tuple[List[FeatureConfigEntry], List[str]]:
    """
    Load feature registry entries from a JSON config file.
    Returns (entries, logs).
    """
    path = Path(os.getenv(FEATURE_CONFIG_ENV, DEFAULT_FEATURE_CONFIG))
    logs: List[str] = []

    if not path.exists():
        logs.append(f"Registry: {path} not found; using built-in defaults")
        return [], logs

    try:
        with path.open() as fh:
            raw = json.load(fh)
        logs.append(f"Registry: loaded {path}")
    except json.JSONDecodeError:
        logs.append(f"Registry: could not parse {path}; using built-in defaults")
        return [], logs

    entries: List[FeatureConfigEntry] = []
    for item in raw.get("features", []):
        feature_id = item.get("id")
        module = item.get("module")
        if not feature_id or not module:
            logs.append("Registry: skipped entry missing id/module")
            continue

        callable_name = item.get("callable", "run")
        label = item.get("label") or f"Notebook[{feature_id}]"
        stage = item.get("stage", "pre")
        if stage not in {"pre", "post"}:
            logs.append(f"Registry: feature {feature_id} has invalid stage '{stage}', defaulting to 'pre'")
            stage = "pre"

        overrides = item.get("overrides", [])
        if not isinstance(overrides, list):
            logs.append(f"Registry: feature {feature_id} overrides must be a list; ignoring overrides")
            overrides = []

        entries.append(
            FeatureConfigEntry(
                feature_id=feature_id,
                module=module,
                callable_name=callable_name,
                label=label,
                stage=stage,
                overrides=overrides,
            )
        )

    if not entries:
        logs.append(f"Registry: {path} contained no valid entries; using built-in defaults")

    return entries, logs
