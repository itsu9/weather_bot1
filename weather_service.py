#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервис для работы с API погоды
"""

import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime
import aiohttp

from config import get_config


logger = logging.getLogger(__name__)


class WeatherService:
    """Сервис для получения данных о погоде"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.config = get_config()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение HTTP сессии"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_request(self, url: str, params: dict) -> Optional[dict]:
        """
        Выполнение HTTP запроса к API
        
        Args:
            url (str): URL для запроса
            params (dict): Параметры запроса
            
        Returns:
            Optional[dict]: Ответ API или None при ошибке
        """
        session = await self._get_session()
        
        for attempt in range(self.config.max_retries):
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        logger.warning(f"Город не найден: {params.get('q')}")
                        return None
                    else:
                        logger.error(f"API ошибка {response.status}: {await response.text()}")
                        
            except asyncio.TimeoutError:
                logger.error(f"Таймаут запроса (попытка {attempt + 1})")
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка клиента (попытка {attempt + 1}): {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка (попытка {attempt + 1}): {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(1)  # Пауза между попытками
        
        return None
    
    async def get_current_weather(self, city: str) -> Optional[Dict]:
        """
        Получение текущей погоды
        
        Args:
            city (str): Название города
            
        Returns:
            Optional[Dict]: Данные о погоде или None
        """
        params = self.config.get_weather_params(city, forecast=False)
        data = await self._make_request(self.config.current_weather_url, params)
        
        if data:
            return self._format_current_weather(data)
        return None
    
    async def get_forecast(self, city: str) -> Optional[Dict]:
        """
        Получение прогноза погоды
        
        Args:
            city (str): Название города
            
        Returns:
            Optional[Dict]: Прогноз погоды или None
        """
        params = self.config.get_weather_params(city, forecast=True)
        data = await self._make_request(self.config.forecast_url, params)
        
        if data:
            return self._format_forecast_data(data)
        return None
    
    def _format_current_weather(self, data: dict) -> Dict:
        """Форматирование данных текущей погоды"""
        try:
            main = data['main']
            weather = data['weather'][0]
            wind = data.get('wind', {})
            clouds = data.get('clouds', {})
            
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(main['temp']),
                'feels_like': round(main['feels_like']),
                'description': weather['description'].title(),
                'icon': weather['icon'],
                'humidity': main['humidity'],
                'pressure': main['pressure'],
                'wind_speed': wind.get('speed', 0),
                'wind_direction': wind.get('deg', 0),
                'cloudiness': clouds.get('all', 0),
                'visibility': data.get('visibility', 0) // 1000,  # в км
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'timezone': data['timezone']
            }
        except KeyError as e:
            logger.error(f"Ошибка форматирования данных погоды: {e}")
            return {}
    
    def _format_forecast_data(self, data: dict) -> Dict:
        """Форматирование данных прогноза"""
        try:
            city_info = data['city']
            forecast_list = data['list']
            
            # Группируем прогноз по дням
            daily_forecasts = {}
            
            for item in forecast_list:
                date_obj = datetime.fromtimestamp(item['dt'])
                date_key = date_obj.strftime('%Y-%m-%d')
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        'date': date_obj,
                        'temp_min': item['main']['temp'],
                        'temp_max': item['main']['temp'],
                        'descriptions': [],
                        'humidity': [],
                        'wind_speeds': [],
                        'main_weather': item['weather'][0]['main'],
                        'icon': item['weather'][0]['icon']
                    }
                
                forecast = daily_forecasts[date_key]
                forecast['temp_min'] = min(forecast['temp_min'], item['main']['temp'])
                forecast['temp_max'] = max(forecast['temp_max'], item['main']['temp'])
                forecast['descriptions'].append(item['weather'][0]['description'])
                forecast['humidity'].append(item['main']['humidity'])
                forecast['wind_speeds'].append(item['wind']['speed'])
            
            # Усредняем данные по дням
            for date_key in daily_forecasts:
                forecast = daily_forecasts[date_key]
                forecast['temp_min'] = round(forecast['temp_min'])
                forecast['temp_max'] = round(forecast['temp_max'])
                forecast['avg_humidity'] = round(sum(forecast['humidity']) / len(forecast['humidity']))
                forecast['avg_wind_speed'] = round(sum(forecast['wind_speeds']) / len(forecast['wind_speeds']), 1)
                
                # Берем самое частое описание
                description_counts = {}
                for desc in forecast['descriptions']:
                    description_counts[desc] = description_counts.get(desc, 0) + 1
                forecast['description'] = max(description_counts.items(), key=lambda x: x[1])[0].title()
            
            return {
                'city': city_info['name'],
                'country': city_info['country'],
                'forecasts': list(daily_forecasts.values())[:5]  # Берем только 5 дней
            }
            
        except KeyError as e:
            logger.error(f"Ошибка форматирования прогноза: {e}")
            return {}
    
    async def close(self):
        """Закрытие HTTP сессии"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_weather_emoji(self, icon_code: str) -> str:
        """
        Получение эмодзи для иконки погоды
        
        Args:
            icon_code (str): Код иконки из API
            
        Returns:
            str: Соответствующий эмодзи
        """
        emoji_map = {
            '01d': '☀️',    # clear sky day
            '01n': '🌙',    # clear sky night
            '02d': '⛅',   # few clouds day
            '02n': '☁️',    # few clouds night
            '03d': '☁️',    # scattered clouds
            '03n': '☁️',    # scattered clouds
            '04d': '☁️',    # broken clouds
            '04n': '☁️',    # broken clouds
            '09d': '🌧️',    # shower rain
            '09n': '🌧️',    # shower rain
            '10d': '🌦️',    # rain day
            '10n': '🌧️',    # rain night
            '11d': '⛈️',    # thunderstorm
            '11n': '⛈️',    # thunderstorm
            '13d': '❄️',    # snow
            '13n': '❄️',    # snow
            '50d': '🌫️',    # mist
            '50n': '🌫️',    # mist
        }
        
        return emoji_map.get(icon_code, '🌤️')
