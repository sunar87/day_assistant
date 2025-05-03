import requests
import os


class Weather:

    def __init__(self, city):
        self.city = city
        self.api_token = os.getenv('WEATHER_API_TOKEN')

    def _weather_request(self):
        if not self.api_token:
            raise ValueError("WEATHER_API_TOKEN не задан в переменных окружения")
        try:
            response = requests.get(
                f'https://api.openweathermap.org/data/2.5/weather?q={self.city}'
                f'&appid={self.api_token}'
                f'&units=metric&lang=ru',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    def weather_output(self):
        data = self._weather_request()
        if not data:
            return "Не удалось получить данные о погоде"
        return (
            f"Погода в {data['name']}:\n"
            f"• Состояние: {data['weather'][0]['description'].capitalize()}\n"
            f"• Температура: {data['main']['temp']}°C\n"
            f"• Ощущается как: {data['main']['feels_like']}°C\n"
            f"• Влажность: {data['main']['humidity']}%\n"
            f"• Давление: {data['main']['pressure']} hPa\n"
            f"• Ветер: {data['wind']['speed']} м/с"
        )
