import signal

from aiogram import types
from aiogram.utils import executor
from django.core.management.base import BaseCommand

from telegram_bot.bot.bot_init import dp
from telegram_bot.bot.weather import Weather


@dp.message_handler(commands=['start'])
async def send_insurance_expiry_info(message: types.Message):
    weather = Weather('saint petersburg')
    msg = weather.weather_output()
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=msg
    )


class Command(BaseCommand):
    help = 'Start Telegram bot'

    def handle(self, *args, **kwargs):
        def shutdown(signal, frame):
            self.stdout.write(self.style.SUCCESS('Shutting down bot...'))
            dp.stop_polling()
            exit(0)
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        self.stdout.write(self.style.SUCCESS('Starting bot...'))
        executor.start_polling(dp, skip_updates=True)
