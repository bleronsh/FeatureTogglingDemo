"""Central feature-to-notebook registry to avoid editing pipeline.py each time."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Callable, List, Set

from app import config_loader, features
from app.notebooks import notifications, quality_legacy, quality_new


@dataclass(frozen=True)
class FeatureEntry:
    feature: str
    handler: Callable[[], None]
    label: str
    overrides: Set[str] = field(default_factory=frozenset)
    stage: str = "pre"  # "pre" runs before publish, "post" runs after publish


# Ordered list controls execution sequence (priority goes top-to-bottom).
_BUILT_IN_REGISTRY: List[FeatureEntry] = [
    FeatureEntry(
        feature=features.FEATURE_NEW_VALIDATION,
        handler=quality_new.run,
        label="Notebook[new_validation]",
        overrides={features.FEATURE_DATA_QUALITY},  # skip legacy if new runs
        stage="pre",
    ),
    FeatureEntry(
        feature=features.FEATURE_DATA_QUALITY,
        handler=quality_legacy.run,
        label="Notebook[quality_legacy]",
        stage="pre",
    ),
    FeatureEntry(
        feature=features.FEATURE_ENRICHMENT,
        handler=lambda: None,  # placeholder; config will supply real handler
        label="Notebook[enrichment]",
        stage="pre",
    ),
    FeatureEntry(
        feature=features.FEATURE_NOTIFICATIONS,
        handler=notifications.run,
        label="Notebook[notifications]",
        stage="post",
    ),
]


def _load_registry_from_config() -> tuple[list[FeatureEntry], list[str]]:
    config_entries, logs = config_loader.load_feature_config()
    registry: list[FeatureEntry] = []

    for entry in config_entries:
        try:
            module = import_module(entry.module)
        except ModuleNotFoundError:
            logs.append(f"Registry: could not import module '{entry.module}' for feature '{entry.feature_id}'")
            continue

        handler = getattr(module, entry.callable_name, None)
        if handler is None:
            logs.append(f"Registry: module '{entry.module}' missing callable '{entry.callable_name}' for feature '{entry.feature_id}'")
            continue

        registry.append(
            FeatureEntry(
                feature=entry.feature_id,
                handler=handler,
                label=entry.label,
                overrides=set(entry.overrides),
                stage=entry.stage,
            )
        )

    if not registry:
        logs.append("Registry: using built-in registry (no valid config entries)")
        registry = list(_BUILT_IN_REGISTRY)

    return registry, logs


FEATURE_REGISTRY, REGISTRY_LOGS = _load_registry_from_config()
