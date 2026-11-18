#Owner::ANIKET::ANHOTRA = MR.Panda
"""Controlled feature switches that default to denying unfinished workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureFlags:
    """Block consequential application features until their gates pass."""

    ai_extraction_enabled: bool = False
    payment_claims_enabled: bool = False
    offline_sync_enabled: bool = False


def current_feature_flags() -> FeatureFlags:
    """Return explicitly disabled pre-pilot features.

    Introduce versioned production configuration only at its approved phase.
    """
    return FeatureFlags()
