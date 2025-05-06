import requests
import os
from datetime import datetime, time


class Weather:
    def __init__(self, city):
        self.city = city
        self.api_token = os.getenv('WEATHER_API_TOKEN')

    def _get_forecast(self):
        """Получаем 5-дневный прогноз с интервалом 3 часа"""
        if not self.api_token:
            raise ValueError("WEATHER_API_TOKEN не задан")

        try:
            response = requests.get(
                'https://api.openweathermap.org/data/2.5/forecast',
                params={
                    'q': self.city,
                    'appid': self.api_token,
                    'units': 'metric',
                    'lang': 'ru'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    def _get_time_period_data(self, forecast_data):
        """Выбираем данные для утра, дня и вечера"""
        periods = {
            'morning': {
                'time_range': (6, 9),
                'temp': None,
                'description': None
            },
            'day': {
                'time_range': (12, 15),
                'temp': None,
                'description': None
            },
            'evening': {
                'time_range': (18, 21),
                'temp': None,
                'description': None
            }
        }

        for forecast in forecast_data['list']:
            forecast_time = datetime.fromtimestamp(forecast['dt']).time()
            for period, data in periods.items():
                start_hour, end_hour = data['time_range']
                if time(start_hour) <= forecast_time < time(end_hour):
                    periods[period]['temp'] = forecast['main']['temp']
                    periods[period]['description'] = forecast[
                        'weather'][0]['description']
                    break
        return periods

    def get_detailed_forecast(self):
        """Получаем детализированный прогноз"""
        forecast_data = self._get_forecast()
        if not forecast_data:
            return None

        return self._get_time_period_data(forecast_data)

    def weather_output(self):
        """Форматируем вывод прогноза"""
        forecast = self.get_detailed_forecast()
        if not forecast:
            return "Не удалось получить прогноз погоды"
        current_weather = self._get_forecast()['list'][0]
        current_city = self._get_forecast()['city']
        return (
            f"{current_city['name']}:\n\n"
            f"• Сейчас: \n{current_weather['main']['temp']}°C, {current_weather['weather'][0]['description']}\n\n"
            f"Утром:\n"
            f"• {forecast['morning']['temp']}°C, {forecast['morning']['description']}\n\n"
            f"Днём:\n"
            f"• {forecast['day']['temp']}°C, {forecast['day']['description']}\n\n"
            f"Вечером:\n"
            f"• {forecast['evening']['temp']}°C, {forecast['evening']['description']}")
