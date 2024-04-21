import logging
import sys

import structlog

from aiogram_bot_template import models
from aiogram_bot_template.data import config


def setup_logger() -> structlog.typing.FilteringBoundLogger:
    logging.basicConfig(
        level=config.LOGGING_LEVEL,
        stream=sys.stdout,
    )
    log: structlog.typing.FilteringBoundLogger = structlog.get_logger(
        structlog.stdlib.BoundLogger,
    )
    shared_processors: list[structlog.typing.Processor] = [
        structlog.processors.add_log_level,
    ]
    processors: list[structlog.typing.Processor] = [*shared_processors]
    if sys.stderr.isatty():
        # Pretty printing when we run in a terminal session.
        # Automatically prints pretty tracebacks when "rich" is installed
        processors.extend(
            [
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.dev.ConsoleRenderer(),
            ],
        )
    else:
        # Print JSON when we run, e.g., in a Docker container.
        # Also print structured tracebacks.
        processors.extend(
            [
                structlog.processors.TimeStamper(fmt=None, utc=True),
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(serializer=models.base.orjson_dumps),
            ],
        )
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(config.LOGGING_LEVEL),
    )
    return log
