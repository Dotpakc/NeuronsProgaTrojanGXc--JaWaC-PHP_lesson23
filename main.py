# pip install aiogram python-decouple
#aiogram == 3.1.1

import asyncio

from random import choice, randint
from decouple import config

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command


API_TOKEN = config('TELEGRAM_API_TOKEN')
ADMIN_ID = config('TELEGRAM_ADMIN_ID')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    print("Starting bot...")
    print("Bot username: @{}".format((await bot.me())))
    await dp.start_polling(bot)

asyncio.run(main())