import requests
from bs4 import BeautifulSoup

ZODIAC_SIGNS = [
    'aries', 'taurus', 'gemini',
    'cancer', 'leo', 'virgo',
    'libra', 'scorpio', 'sagittarius',
    'capricorn', 'aquarius', 'pisces'
]


def get_horoscope(zodiac_title: str) -> str:
    zodiac_title = zodiac_title.lower()
    if zodiac_title not in ZODIAC_SIGNS:
        return 'Неизвестный знак зодиака'
    url = 'https://ignio.com/r/export/utf/xml/daily/com.xml'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        horoscope = soup.find('horo')
        if not horoscope:
            return "Не удалось найти данные гороскопа"
        zodiac_tag = horoscope.find(zodiac_title)
        if not zodiac_tag:
            return f"Данные для {zodiac_title} не найдены"
        today = zodiac_tag.find('today')
        if today:
            return today.text.strip()
        else:
            return "Прогноз на сегодня не доступен"
    except requests.exceptions.RequestException as e:
        return f"Ошибка при запросе данных: {e}"
    except Exception as e:
        return f"Произошла ошибка: {e}"


print(get_horoscope('gemini'))
