import logging
import sys

import structlog

import models.base
from data import config


def setup_logger() -> structlog.typing.FilteringBoundLogger:
    logging.basicConfig(
        level=config.LOGGING_LEVEL,
        stream=sys.stdout,
    )
    log: structlog.typing.FilteringBoundLogger = structlog.get_logger(wrapper_class=structlog.stdlib.BoundLogger)
    shared_processors: list[structlog.typing.Processor] = [
        structlog.processors.add_log_level
    ]
    if sys.stderr.isatty():
        # Pretty printing when we run in a terminal session.
        # Automatically prints pretty tracebacks when "rich" is installed
        processors = shared_processors + [
            structlog.processors.TimeStamper(fmt='iso', utc=True),
            structlog.dev.ConsoleRenderer()
        ]
    else:
        # Print JSON when we run, e.g., in a Docker container.
        # Also print structured tracebacks.
        processors = shared_processors + [
            structlog.processors.TimeStamper(fmt=None, utc=True),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(serializer=models.base.orjson_dumps)
        ]
    structlog.configure(processors)
    return log
