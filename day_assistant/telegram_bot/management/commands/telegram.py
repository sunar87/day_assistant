import signal
import logging
import asyncio

from aiogram import (
    types,
    Bot
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import (
    State,
    StatesGroup
)
from aiogram.utils import executor
from django.core.management.base import BaseCommand
from django.conf import settings  # noqa
from asgiref.sync import sync_to_async
from django.db import transaction

from telegram_bot.bot.bot_init import dp
from telegram_bot.bot.markups import (
    start_keyboard,
    already_registered_keyboard,
    horoscope_keyboard
)
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
    user_exists = await sync_to_async(
        User.objects.filter(
            telegram_id=message.from_user.id
        ).exists)()

    if user_exists:
        await message.answer(
            "Вы уже зарегистрированы!",
            reply_markup=already_registered_keyboard
        )
    else:
        await message.answer(
            "Привет! Нажми кнопку ниже, чтобы зарегистрироваться.",
            reply_markup=start_keyboard
        )


@dp.message_handler(Text(equals="Регистрация"))
async def start_registration(message: types.Message):
    user_exists = await sync_to_async(
        User.objects.filter(
            telegram_id=message.from_user.id
        ).exists)()
    if user_exists:
        return await message.answer('Вы уже зарегистрированы')
    await RegistrationStates.waiting_for_city.set()
    await message.answer("Введите ваш город:")


@dp.message_handler(state=RegistrationStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await RegistrationStates.next()
    await message.answer(
        "Выберите ваш знак зодиака:",
        reply_markup=horoscope_keyboard
    )


@dp.message_handler(state=RegistrationStates.waiting_for_zodiac)
async def process_zodiac(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        city = data['city']
        zodiac = message.text.split(' ')[0].lower()
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
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя: {e}")
        await message.answer("⚠️ Произошла ошибка при сохранении данных.")
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


@dp.message_handler(Text(equals="Подключить уведомления"))
async def start_notifications(message: types.Message):
    user_exists = await sync_to_async(
        User.objects.filter(telegram_id=message.from_user.id).exists
    )()
    if not user_exists:
        return await message.answer('Для начала зарегистрируйтесь!')
    try:
        def update_user():
            with transaction.atomic():
                user = User.objects.select_for_update().get(
                    telegram_id=message.from_user.id
                )
                user.notifications = True
                user.save()
        await sync_to_async(update_user)()
        await message.answer('Уведомления подключены!')
    except Exception as e:
        await message.answer('Произошла ошибка при обновлении')
        logger.error(f"Ошибка обновления уведомлений: {e}")


async def daily_info(bot: Bot):
    users = await sync_to_async(list)(User.objects.filter(notifications=True))
    for user in users:
        try:
            weather = await sync_to_async(Weather)(
                user.city
            )
            horoscope = await sync_to_async(Horoscope)(
                user.zodiac
            )
            weather_info = await sync_to_async(weather.weather_output)()
            horoscope_info = await sync_to_async(horoscope.get_horoscope)()

            msg = (
                f"🌤 Погода в {user.city}:\n{weather_info}\n\n"
                f"♉ Гороскоп для {user.zodiac}:\n{horoscope_info}"
            )
            await bot.send_message(
                chat_id=user.telegram_id,
                text=msg
            )
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Ошибка отправки для {user.telegram_id}: {e}")


@dp.message_handler(commands=["test23"])
async def cmd_send_daily(message: types.Message):
    await daily_info(message.bot)


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
