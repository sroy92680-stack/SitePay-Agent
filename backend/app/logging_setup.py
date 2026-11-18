#Owner::ANIKET::ANHOTRA = MR.Panda
"""Structured application logging without request body or token inclusion."""

from __future__ import annotations

import logging


def configure_logging(environment: str) -> None:
    """Use a consistent event logger without recording password payloads.

    Service code must log event identifiers, never raw evidence or credentials.
    """
    log_level = logging.DEBUG if environment == "development" else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
