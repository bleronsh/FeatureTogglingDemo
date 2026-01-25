"""Central feature-to-notebook registry to avoid editing pipeline.py each time."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Set

from app import features
from app.notebooks import enrichment, notifications, quality_legacy, quality_new


@dataclass(frozen=True)
class FeatureEntry:
    feature: str
    handler: Callable[[], None]
    label: str
    overrides: Set[str] = field(default_factory=frozenset)
    stage: str = "pre"  # "pre" runs before publish, "post" runs after publish


# Ordered list controls execution sequence (priority goes top-to-bottom).
FEATURE_REGISTRY: List[FeatureEntry] = [
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
        handler=enrichment.run,
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
