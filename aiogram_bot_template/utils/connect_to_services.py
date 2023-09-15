import asyncpg
import redis
import structlog
import tenacity
from redis.asyncio import ConnectionPool, Redis
from tenacity import _utils

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
        "Retrying {callback} in {sleep} seconds as it {verb} {value}".format(
            callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
            sleep=retry_state.next_action.sleep,  # type: ignore[union-attr]
            verb=verb,
            value=value,
        ),
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        sleep=retry_state.next_action.sleep,  # type: ignore[union-attr]
        verb=verb,
        value=value,
    )


def after_log(retry_state: tenacity.RetryCallState) -> None:
    logger = retry_state.kwargs["logger"]
    logger.info(
        "Finished call to {callback!r} after {time:.2f}, this was the {attempt} time calling it.".format(  # type: ignore[str-format]
            callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
            time=retry_state.seconds_since_start,
            attempt=_utils.to_ordinal(retry_state.attempt_number),
        ),
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
    logger: structlog.typing.FilteringBoundLogger,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> asyncpg.Pool:
    db_pool = await asyncpg.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
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
async def wait_redis_pool(
    logger: structlog.typing.FilteringBoundLogger,
    host: str,
    port: int,
    password: str,
    database: int,
) -> redis.asyncio.Redis:  # type: ignore[type-arg]
    redis_pool: redis.asyncio.Redis = Redis(  # type: ignore[type-arg]
        connection_pool=ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=database,
        )
    )
    version = await redis_pool.info("server")
    logger.debug("Connected to Redis.", version=version["redis_version"])
    return redis_pool
