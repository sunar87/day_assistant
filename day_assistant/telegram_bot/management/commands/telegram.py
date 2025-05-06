import signal
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from django.core.management.base import BaseCommand
from django.conf import settings  # noqa
from asgiref.sync import sync_to_async

from telegram_bot.bot.bot_init import dp
from telegram_bot.bot.markups import start_keyboard
from telegram_bot.bot.weather import Weather
from telegram_bot.bot.horoscope import Horoscope
from telegram_bot.models import User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegistrationStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_zodiac = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Нажми кнопку ниже, чтобы зарегистрироваться.",
        reply_markup=start_keyboard
    )


@dp.message_handler(Text(equals="Регистрация"))
async def start_registration(message: types.Message):
    await RegistrationStates.waiting_for_city.set()
    await message.answer("Введите ваш город:")


@dp.message_handler(state=RegistrationStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    await RegistrationStates.next()
    await message.answer("Теперь введите ваш знак зодиака:")


@dp.message_handler(state=RegistrationStates.waiting_for_zodiac)
async def process_zodiac(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        city = data['city']
        zodiac = message.text

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    try:
        user, created = await sync_to_async(User.objects.get_or_create)(
            telegram_id=user_id,
            defaults={
                'telegram_username': username,
                'city': city,
                'zodiac': zodiac
            }
        )
        logger.info(
            f"Пользователь {'создан' if created else 'обновлён'}: {user}")
        if user:
            await message.answer("⚠️ Вы уже зарегестрированы.")
            await state.finish()
            return
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя: {e}")
        await message.answer("⚠️ Произошла ошибка при сохранении данных. Попробуйте позже.")
        await state.finish()
        return
    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"Ваши данные:\n"
        f"ID: {user_id}\n"
        f"Имя: {username}\n"
        f"Город: {city}\n"
        f"Знак зодиака: {zodiac}",
        reply_markup=start_keyboard
    )

    await state.finish()


async def send_insurance_expiry_info(message: types.Message):
    weather = Weather('saint petersburg')
    horoscope = Horoscope('gemini')
    msg = f'Погода:\n{weather.weather_output()}\n\nВаш гороскоп на сегодня:\n{horoscope.get_horoscope()}'
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
