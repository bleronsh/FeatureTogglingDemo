"""
Stable feature flag identifiers used across environments.

These strings are treated as contract values: code and configuration
agree on the same names, and they are not tied to branches or tags.
"""

from typing import Optional

# Run enhanced validation steps (e.g., schema and freshness checks)
FEATURE_DATA_QUALITY = "data_quality_checks"

# Enrich the dataset with an experimental scoring routine (now baseline)
FEATURE_ENRICHMENT = "experimental_enrichment"

# Send downstream notifications when a run succeeds
FEATURE_NOTIFICATIONS = "notify_ops"

# Run new validation logic (e.g., refactored notebook)
FEATURE_NEW_VALIDATION = "new_validation"

# All supported features, kept in one place for easy reference
ALL_FEATURES = {
    FEATURE_DATA_QUALITY,
    FEATURE_ENRICHMENT,
    FEATURE_NOTIFICATIONS,
    FEATURE_NEW_VALIDATION,
}


def parse_feature_flags(raw: Optional[str]) -> set[str]:
    """
    Parse a comma-separated string of feature names into a set.
    Empty strings and whitespace are ignored.
    """
    if raw is None:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}
