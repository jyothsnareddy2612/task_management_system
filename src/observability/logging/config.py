import logging
import sys

import structlog

from src.api.middleware.request_context import request_id_ctx


def add_request_id(_: object, __: str, event_dict: dict[str, object]) -> dict[str, object]:
    event_dict["request_id"] = request_id_ctx.get()
    return event_dict


def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            add_request_id,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

