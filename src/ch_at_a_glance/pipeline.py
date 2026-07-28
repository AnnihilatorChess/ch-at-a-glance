"""Orchestrates collectors -> normalize -> upsert. One failing collector never
blocks the rest of the run."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from ch_at_a_glance.config import INDICATOR_REGISTRY, IndicatorDefinition
from ch_at_a_glance.db import session_scope
from ch_at_a_glance.models import Indicator, Observation

logger = logging.getLogger(__name__)


def _get_or_create_indicator(session: Session, definition: IndicatorDefinition) -> Indicator:
    indicator = session.execute(
        select(Indicator).where(Indicator.slug == definition.slug)
    ).scalar_one_or_none()
    if indicator is None:
        indicator = Indicator(
            slug=definition.slug,
            label=definition.label,
            category=definition.category,
            unit=definition.unit,
            direction=definition.direction,
            note=definition.note,
            source_url=definition.source_url,
        )
        session.add(indicator)
        session.flush()
        return indicator

    indicator.label = definition.label
    indicator.category = definition.category
    indicator.unit = definition.unit
    indicator.direction = definition.direction
    indicator.note = definition.note
    indicator.source_url = definition.source_url
    return indicator


def run_update(registry: list[IndicatorDefinition] | None = None) -> dict[str, str]:
    """Run every registered collector. Returns {slug: status}, never raises."""
    results: dict[str, str] = {}
    for definition in registry if registry is not None else INDICATOR_REGISTRY:
        try:
            rows = definition.collector()
        except Exception:
            logger.exception("Collector failed for %s", definition.slug)
            results[definition.slug] = "failed"
            continue

        with session_scope() as session:
            indicator = _get_or_create_indicator(session, definition)
            existing_dates = {obs.date for obs in indicator.observations}
            new_count = 0
            for row in rows:
                if row.date in existing_dates:
                    continue
                session.add(Observation(indicator_id=indicator.id, date=row.date, value=row.value))
                new_count += 1

        logger.info("%s: %d new observation(s)", definition.slug, new_count)
        results[definition.slug] = f"ok ({new_count} new)"
    return results
