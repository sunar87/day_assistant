import requests
from bs4 import BeautifulSoup


class Horoscope:
    ZODIAC_SIGNS = [
        'aries', 'taurus', 'gemini',
        'cancer', 'leo', 'virgo',
        'libra', 'scorpio', 'sagittarius',
        'capricorn', 'aquarius', 'pisces'
    ]

    def __init__(self, zodiac: str):
        self.zodiac = zodiac.lower()
        self.url = 'https://ignio.com/r/export/utf/xml/daily/com.xml'
        if self.zodiac not in self.ZODIAC_SIGNS:
            raise ValueError('Неизвестный знак зодиака')

    def get_horoscope(self) -> str:
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')
            horoscope = soup.find('horo')
            if not horoscope:
                return "Не удалось найти данные гороскопа"
            zodiac_tag = horoscope.find(self.zodiac)
            if not zodiac_tag:
                return f"Данные для {self.zodiac} не найдены"
            today = zodiac_tag.find('today')
            if today:
                return today.text.strip()
            else:
                return "Прогноз на сегодня не доступен"
        except requests.exceptions.RequestException as e:
            return f"Ошибка при запросе данных: {e}"
        except Exception as e:
            return f"Произошла ошибка: {e}"
