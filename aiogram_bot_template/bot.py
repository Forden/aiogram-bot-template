import asyncio

import aiojobs
import asyncpg as asyncpg
import orjson
import redis
import structlog
import tenacity
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web
from redis.asyncio import Redis
from tenacity import _utils

from aiogram_bot_template import handlers, utils, web_handlers
from aiogram_bot_template.data import config
from aiogram_bot_template.middlewares import StructLoggingMiddleware

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
            callback=_utils.get_callback_name(retry_state.fn),  # type: ignore
            sleep=retry_state.next_action.sleep,  # type: ignore
            verb=verb,
            value=value,
        ),
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore
        sleep=retry_state.next_action.sleep,  # type: ignore
        verb=verb,
        value=value,
    )


def after_log(retry_state: tenacity.RetryCallState) -> None:
    logger = retry_state.kwargs["logger"]
    logger.info(
        "Finished call to {callback!r} after {time:.2f}, this was the {attempt} time calling it.".format(
            callback=_utils.get_callback_name(retry_state.fn),  # type: ignore
            time=retry_state.seconds_since_start,
            attempt=_utils.to_ordinal(retry_state.attempt_number),
        ),
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore
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
    db_pool: asyncpg.Pool = await asyncpg.create_pool(
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
    redis_pool: redis.asyncio.Redis = redis.asyncio.Redis(  # type: ignore[type-arg]
        connection_pool=redis.asyncio.ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=database,
        )
    )
    version = await redis_pool.info("server")
    logger.debug("Connected to Redis.", version=version["redis_version"])
    return redis_pool


async def create_db_connections(dp: Dispatcher) -> None:
    logger: structlog.typing.FilteringBoundLogger = dp["business_logger"]
    logger.debug("Connecting to PostgreSQL", db="main")
    try:
        db_pool = await wait_postgres(
            logger=dp["db_logger"],
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE,
        )
    except tenacity.RetryError:
        logger.error("Failed to connect to PostgreSQL", db="main")
        exit(1)
    else:
        logger.debug("Succesfully connected to PostgreSQL", db="main")
    dp["db_pool"] = db_pool
    logger.debug("Connecting to Redis")
    try:
        redis_pool = await wait_redis_pool(
            logger=dp["cache_logger"],
            host=config.CACHE_HOST,
            password=config.CACHE_PASSWORD,
            port=config.CACHE_PORT,
            database=0,
        )
    except tenacity.RetryError:
        logger.error("Failed to connect to Redis")
        exit(1)
    else:
        logger.debug("Succesfully connected to Redis")
    dp["cache_pool"] = redis_pool

    dp["temp_bot_cloud_session"] = AiohttpSession(json_loads=orjson.loads)
    if config.USE_CUSTOM_API_SERVER:
        dp["temp_bot_local_session"] = AiohttpSession(
            api=TelegramAPIServer(
                base=config.CUSTOM_API_SERVER_BASE,
                file=config.CUSTOM_API_SERVER_FILE,
                is_local=config.CUSTOM_API_SERVER_IS_LOCAL,
            ),
            json_loads=orjson.loads,
        )


async def close_db_connections(dp: Dispatcher) -> None:
    if "temp_bot_cloud_session" in dp.workflow_data:
        temp_bot_cloud_session: AiohttpSession = dp["temp_bot_cloud_session"]
        await temp_bot_cloud_session.close()
    if "temp_bot_local_session" in dp.workflow_data:
        temp_bot_local_session: AiohttpSession = dp["temp_bot_local_session"]
        await temp_bot_local_session.close()
    if "db_pool" in dp.workflow_data:
        db_pool: asyncpg.Pool = dp["db_pool"]
        await db_pool.close()
    if "cache_pool" in dp.workflow_data:
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]  # type: ignore[type-arg]
        await cache_pool.close()


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.user.prepare_router())


def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.outer_middleware(
        StructLoggingMiddleware(
            logger=dp["aiogram_logger"], logger_init_values=dp["aiogram_logger_init"]
        )
    )


def setup_logging(dp: Dispatcher) -> None:
    dp["business_logger_init"] = {"type": "business"}
    dp["business_logger"] = utils.logging.setup_logger().bind(
        **dp["business_logger_init"]
    )
    dp["aiogram_logger_init"] = {"type": "aiogram"}
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(
        **dp["aiogram_logger_init"]
    )
    dp["db_logger_init"] = {"type": "db"}
    dp["db_logger"] = utils.logging.setup_logger().bind(**dp["db_logger_init"])
    dp["cache_logger_init"] = {"type": "cache"}
    dp["cache_logger"] = utils.logging.setup_logger().bind(**dp["cache_logger_init"])


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:  # dirty
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                dp["aiogram_logger"].info(
                    f"Waiting for {scheduler.pending_count} tasks to complete"
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(
        webhook_url=config.MAIN_WEBHOOK_ADDRESS
    )
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=config.MAIN_WEBHOOK_ADDRESS.format(token=config.BOT_TOKEN),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=config.MAIN_WEBHOOK_SECRET_TOKEN,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


async def setup_aiohttp_app(bot: Bot, dp: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app


def main() -> None:
    if config.USE_CUSTOM_API_SERVER:
        session = AiohttpSession(
            api=TelegramAPIServer(
                base=config.CUSTOM_API_SERVER_BASE,
                file=config.CUSTOM_API_SERVER_FILE,
                is_local=config.CUSTOM_API_SERVER_IS_LOCAL,
            ),
            json_loads=orjson.loads,
        )
    else:
        session = AiohttpSession(json_loads=orjson.loads)
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML", session=session)

    dp = Dispatcher(
        storage=RedisStorage(
            redis=Redis(
                host=config.FSM_HOST,
                password=config.FSM_PASSWORD,
                port=config.FSM_PORT,
                db=0,
            )
        )
    )

    if config.USE_WEBHOOK:
        dp.startup.register(aiogram_on_startup_webhook)
        dp.shutdown.register(aiogram_on_shutdown_webhook)
        web.run_app(
            asyncio.run(setup_aiohttp_app(bot, dp)),
            handle_signals=True,
            host=config.MAIN_WEBHOOK_LISTENING_HOST,
            port=config.MAIN_WEBHOOK_LISTENING_PORT,
        )
    else:
        dp.startup.register(aiogram_on_startup_polling)
        dp.shutdown.register(aiogram_on_shutdown_polling)
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
