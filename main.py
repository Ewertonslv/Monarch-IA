"""Monarch AI — entry point.

Starts both the FastAPI web interface and the Telegram bot concurrently.
"""
import asyncio
import logging
import signal
import sys

import uvicorn

from config import config
from core.orchestrator import Orchestrator
from storage.database import Database
from interfaces.telegram_bot import TelegramBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    db = Database(config.database_url)
    await db.init()
    orchestrator = Orchestrator(db)

    telegram = TelegramBot(db=db, orchestrator=orchestrator)

    # Wire Telegram bot into Orchestrator so approval gates send notifications
    orchestrator.set_telegram_bot(telegram)

    # Inject shared db + orchestrator into the web app module
    import interfaces.web.app as web_module
    web_module._db = db
    web_module._orchestrator = orchestrator

    uvicorn_config = uvicorn.Config(
        "interfaces.web.app:app",
        host="0.0.0.0",
        port=config.web_port,
        log_level="info",
    )
    server = uvicorn.Server(uvicorn_config)

    stop_event = asyncio.Event()

    def _handle_signal(*_):
        logger.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_event_loop().add_signal_handler(sig, _handle_signal)
        except NotImplementedError:  # Windows
            signal.signal(sig, _handle_signal)

    logger.info("Starting Monarch AI on port %d", config.web_port)

    async def run_server():
        await server.serve()

    async def run_telegram():
        try:
            await telegram.start_polling()
            await stop_event.wait()
        finally:
            await telegram.stop()

    tasks = [
        asyncio.create_task(run_server()),
        asyncio.create_task(run_telegram()),
    ]

    try:
        await stop_event.wait()
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await db.close()
        logger.info("Monarch AI stopped.")


if __name__ == "__main__":
    asyncio.run(main())
