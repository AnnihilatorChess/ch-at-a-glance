"""Shared collector contract and HTTP retry helper.

A collector is a plain callable returning normalized rows for one indicator.
Deliberately a Protocol/type alias rather than a base class: sources that
don't fit an HTTP-client shape (e.g. an xlsx download) shouldn't have to
fight an inheritance hierarchy designed around the common case.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RawObservation:
    date: date
    value: float


Collector = Callable[[], list[RawObservation]]


def fetch_with_retry(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    retries: int = 3,
    backoff_seconds: float = 1.5,
    **kwargs: object,
) -> httpx.Response:
    """Request with exponential backoff. Raises the last error if all attempts fail."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            response = client.request(method, url, **kwargs)  # type: ignore[arg-type]
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            last_exc = exc
            logger.warning(
                "Request failed (attempt %d/%d): %s %s -> %s",
                attempt + 1,
                retries,
                method,
                url,
                exc,
            )
            if attempt < retries - 1:
                time.sleep(backoff_seconds**attempt)
    assert last_exc is not None
    raise last_exc
