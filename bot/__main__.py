import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand

from .config import load_config
from .db import Database
from .handlers import setup_router
from .llm import LLM


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = load_config()
    db = Database(config.db_path)
    llm = LLM(config)

    session = AiohttpSession(proxy=config.proxy_url) if config.proxy_url else AiohttpSession()
    bot = Bot(token=config.bot_token, session=session)
    dp = Dispatcher()
    dp.include_router(setup_router(config, db, llm))

    await bot.set_my_commands([
        BotCommand(command="start", description="Start / Начать"),
        BotCommand(command="chooselanguage", description="Choose language / Выбрать язык"),
        BotCommand(command="help", description="Help / Помощь"),
    ])
    logging.info("Help in Moscow bot started, model %s, web search %s", config.model, config.web_search)
    try:
        await dp.start_polling(bot)
    finally:
        await llm.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
