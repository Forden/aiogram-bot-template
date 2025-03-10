import asyncpg
import redis.asyncio as redis
import structlog
import tenacity
from tenacity import _utils  # noqa: PLC2701

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30


def before_log(retry_state: tenacity.RetryCallState) -> None:
    if retry_state.outcome is None:
        return
    if retry_state.outcome.failed:
        verb, value = "raised", retry_state.outcome.exception()
    else:
        verb, value = "returned", retry_state.outcome.result()
    logger = retry_state.kwargs["logger"]
    logger.info(
        "Retrying %s in %s seconds as it %s %s",
        _utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        retry_state.next_action.sleep,  # type: ignore[union-attr]
        verb,
        value,
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        sleep=retry_state.next_action.sleep,  # type: ignore[union-attr]
        verb=verb,
        value=value,
    )


def after_log(retry_state: tenacity.RetryCallState) -> None:
    logger = retry_state.kwargs["logger"]
    logger.info(
        "Finished call to %s after %s, this was the %s time calling it.",
        _utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        f"{retry_state.seconds_since_start:.2f}",
        _utils.to_ordinal(retry_state.attempt_number),
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        time=retry_state.seconds_since_start,
        attempt=_utils.to_ordinal(retry_state.attempt_number),
    )


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log,
)
async def wait_postgres(
    *,
    logger: structlog.typing.FilteringBoundLogger,
    dsn: str,
) -> asyncpg.Pool:
    db_pool = await asyncpg.create_pool(
        dsn=dsn,
        min_size=1,
        max_size=3,
    )
    version = await db_pool.fetchrow("SELECT version() as ver;")
    logger.debug("Connected to PostgreSQL.", version=version["ver"])
    return db_pool


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log,
)
async def wait_redis_pool(  # noqa: PLR0913
    *,
    logger: structlog.typing.FilteringBoundLogger,
    host: str,
    port: int,
    username: str,
    password: str,
    database: int,
) -> redis.Redis:
    redis_connection: redis.Redis = redis.Redis(
        host=host,
        port=port,
        username=username,
        password=password,
        db=database,
        auto_close_connection_pool=True,
        decode_responses=True,
        protocol=3,
        socket_timeout=10,  # limits any command to 10 seconds as per https://github.com/redis/redis-py/issues/722
        socket_keepalive=True,  # tries to keep connection alive, not 100% guarantee
    )
    version = await redis_connection.info("server")
    logger.debug("Connected to Redis.", version=version["redis_version"])
    return redis_connection
