import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from bot.db import init_db
from bot.handlers.group import router as group_router
from bot.handlers.parcipant import router as parcipant_router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("SECRET_SANTA_DB", "secret_santa.db")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

dp.include_routers(group_router, parcipant_router)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Secret Santa bot работает!")


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

