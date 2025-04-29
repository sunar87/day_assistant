import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.conf import settings

tg_token = settings.BOT_TOKEN

bot = Bot(token=tg_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
