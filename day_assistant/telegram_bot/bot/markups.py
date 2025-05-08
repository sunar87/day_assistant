from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Регистрация")]
    ],
    resize_keyboard=True
)

already_registered_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подключить уведомления")]
    ],
    resize_keyboard=True
)

horoscope_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Aries (Овен)"),
            KeyboardButton(text="Libra (Весы)")
        ],
        [
            KeyboardButton(text="Taurus (Телец)"),
            KeyboardButton(text="Scorpio (Скорпион)")
        ],
        [
            KeyboardButton(text="Gemini (Близнецы)"),
            KeyboardButton(text="Sagittarius (Стрелец)")
        ],
        [
            KeyboardButton(text="Cancer (Рак)"),
            KeyboardButton(text="Capricorn (Козерог)")
        ],
        [
            KeyboardButton(text="Leo (Лев)"),
            KeyboardButton(text="Aquarius (Водолей)")
        ],
        [
            KeyboardButton(text="Virgo (Дева)"),
            KeyboardButton(text="Pisces (Рыбы)")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
