import datetime

import requests


class WeatherService:
    def __init__(self, api_key, geo_coordinates, units='imperial'):

        lat, lon = map(lambda x: x.strip(), geo_coordinates.split(','))
        self.full_url = (
            f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}'
            f'&units={units}'
            f'&appid={api_key}')

        self.temp_display_unit = {
            'metric': '°C',
            'imperial': '°F'
        }[units]

    def get_weather_data(self):
        response = requests.get(self.full_url)
        response.raise_for_status()
        data = response.json()

        temperature = str(round(data['main']['temp'])) + self.temp_display_unit
        feels_like = str(round(data['main']['feels_like'])) + self.temp_display_unit
        high = str(round(data['main']['temp_max'])) + "&deg; F"
        low = str(round(data['main']['temp_min'])) + "&deg; F"
        condition_str = data['weather'][0]['description']

        weather_sub_description = f'Feels like {feels_like}. {condition_str}'

        return {'temperature': temperature,
                'weather_sub_description': weather_sub_description.capitalize(),
                'fetched_at': datetime.datetime.now()
                }



