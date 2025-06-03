#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для форматирования сообщений
"""

from datetime import datetime
from typing import Dict, List
import pytz

# from weather_service import WeatherService  # Избегаем циклического импорта


def format_weather_message(weather_data: Dict) -> str:
    """
    Форматирование сообщения с текущей погодой
    
    Args:
        weather_data (Dict): Данные о погоде
        
    Returns:
        str: Отформатированное сообщение
    """
    if not weather_data:
        return "❌ Данные о погоде недоступны"
    
    # Получаем эмодзи для погоды
    weather_emoji = get_weather_emoji(weather_data.get('icon', ''))
    
    # Определяем направление ветра
    wind_direction = get_wind_direction(weather_data.get('wind_direction', 0))
    
    # Форматируем время восхода и заката
    sunrise = weather_data.get('sunrise', datetime.now()).strftime('%H:%M')
    sunset = weather_data.get('sunset', datetime.now()).strftime('%H:%M')
    
    message = f"""
{weather_emoji} <b>{weather_data.get('city', 'Неизвестно')}, {weather_data.get('country', '')}</b>

🌡️ <b>Температура:</b> {weather_data.get('temperature', 0)}°C
🤚 <b>Ощущается как:</b> {weather_data.get('feels_like', 0)}°C
📝 <b>Описание:</b> {weather_data.get('description', 'Неизвестно')}

💨 <b>Ветер:</b> {weather_data.get('wind_speed', 0)} м/с {wind_direction}
💧 <b>Влажность:</b> {weather_data.get('humidity', 0)}%
📊 <b>Давление:</b> {weather_data.get('pressure', 0)} гПа
☁️ <b>Облачность:</b> {weather_data.get('cloudiness', 0)}%
👁️ <b>Видимость:</b> {weather_data.get('visibility', 0)} км

🌅 <b>Восход:</b> {sunrise}
🌇 <b>Закат:</b> {sunset}

<i>Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>
"""
    
    return message.strip()


def format_forecast_message(forecast_data: Dict) -> str:
    """
    Форматирование сообщения с прогнозом погоды
    
    Args:
        forecast_data (Dict): Данные прогноза
        
    Returns:
        str: Отформатированное сообщение
    """
    if not forecast_data or not forecast_data.get('forecasts'):
        return "❌ Данные прогноза недоступны"
    
    city = forecast_data.get('city', 'Неизвестно')
    country = forecast_data.get('country', '')
    forecasts = forecast_data.get('forecasts', [])
    
    message = f"📅 <b>Прогноз погоды на 5 дней</b>\n"
    message += f"📍 <b>{city}, {country}</b>\n\n"
    
    for i, forecast in enumerate(forecasts):
        date_obj = forecast.get('date', datetime.now())
        
        # Определяем день недели
        if i == 0:
            day_name = "Сегодня"
        elif i == 1:
            day_name = "Завтра"
        else:
            day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            day_name = day_names[date_obj.weekday()]
        
        # Получаем эмодзи
        weather_emoji = get_weather_emoji(forecast.get('icon', ''))
        
        # Форматируем дату
        date_str = date_obj.strftime('%d.%m')
        
        message += f"{weather_emoji} <b>{day_name}, {date_str}</b>\n"
        message += f"🌡️ {forecast.get('temp_min', 0)}°...{forecast.get('temp_max', 0)}°C\n"
        message += f"📝 {forecast.get('description', 'Неизвестно')}\n"
        message += f"💧 {forecast.get('avg_humidity', 0)}% | 💨 {forecast.get('avg_wind_speed', 0)} м/с\n\n"
    
    message += f"<i>Прогноз обновлен: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"
    
    return message.strip()


def get_weather_emoji(icon_code: str) -> str:
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


def get_wind_direction(degrees: float) -> str:
    """
    Получение направления ветра по градусам
    
    Args:
        degrees (float): Градусы направления ветра
        
    Returns:
        str: Направление ветра
    """
    directions = [
        "С", "ССВ", "СВ", "ВСВ",
        "В", "ВЮВ", "ЮВ", "ЮЮВ",
        "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ",
        "З", "ЗСЗ", "СЗ", "ССЗ"
    ]
    
    # Нормализуем градусы к диапазону 0-360
    degrees = degrees % 360
    
    # Определяем индекс направления
    index = round(degrees / 22.5) % 16
    
    return directions[index]


def format_temperature(temp: float, units: str = "metric") -> str:
    """
    Форматирование температуры
    
    Args:
        temp (float): Температура
        units (str): Единицы измерения
        
    Returns:
        str: Отформатированная температура
    """
    if units == "metric":
        return f"{round(temp)}°C"
    elif units == "imperial":
        return f"{round(temp)}°F"
    else:  # kelvin
        return f"{round(temp)}K"


def get_weather_advice(weather_data: Dict) -> str:
    """
    Получение советов по погоде
    
    Args:
        weather_data (Dict): Данные о погоде
        
    Returns:
        str: Совет по погоде
    """
    temp = weather_data.get('temperature', 0)
    description = weather_data.get('description', '').lower()
    wind_speed = weather_data.get('wind_speed', 0)
    humidity = weather_data.get('humidity', 0)
    
    advice = []
    
    # Советы по температуре
    if temp < -10:
        advice.append("🧥 Очень холодно! Одевайтесь теплее")
    elif temp < 0:
        advice.append("❄️ Холодно, не забудьте куртку")
    elif temp < 10:
        advice.append("🧥 Прохладно, возьмите теплую одежду")
    elif temp > 25:
        advice.append("☀️ Жарко! Не забудьте о солнцезащите")
    elif temp > 30:
        advice.append("🌡️ Очень жарко! Пейте больше воды")
    
    # Советы по осадкам
    if any(word in description for word in ['дождь', 'rain', 'shower']):
        advice.append("☂️ Возьмите зонт!")
    elif 'снег' in description or 'snow' in description:
        advice.append("❄️ Снег! Обувь с хорошим протектором")
    elif 'туман' in description or 'mist' in description:
        advice.append("🌫️ Туман, будьте осторожны на дороге")
    
    # Советы по ветру
    if wind_speed > 10:
        advice.append("💨 Сильный ветер! Закрепите легкие вещи")
    
    # Советы по влажности
    if humidity > 80:
        advice.append("💧 Высокая влажность, может быть душно")
    
    return " | ".join(advice) if advice else "🌤️ Хорошая погода для прогулок!"


def format_time_with_timezone(timestamp: datetime, timezone_offset: int) -> str:
    """
    Форматирование времени с учетом часового пояса
    
    Args:
        timestamp (datetime): Временная метка
        timezone_offset (int): Смещение часового пояса в секундах
        
    Returns:
        str: Отформатированное время
    """
    # Создаем объект часового пояса
    tz = pytz.FixedOffset(timezone_offset // 60)
    
    # Применяем часовой пояс
    local_time = timestamp.replace(tzinfo=pytz.UTC).astimezone(tz)
    
    return local_time.strftime('%H:%M')


def get_comfort_level(temp: float, humidity: int) -> tuple:
    """
    Определение уровня комфорта погоды
    
    Args:
        temp (float): Температура
        humidity (int): Влажность
        
    Returns:
        tuple: (уровень_комфорта, описание)
    """
    # Индекс жары (упрощенный)
    if temp >= 20 and temp <= 26 and humidity >= 40 and humidity <= 60:
        return ("🟢", "Комфортно")
    elif temp >= 15 and temp <= 30 and humidity >= 30 and humidity <= 70:
        return ("🟡", "Приемлемо")
    elif temp < 0 or temp > 35 or humidity > 85:
        return ("🔴", "Некомфортно")
    else:
        return ("🟠", "Терпимо")


def format_detailed_forecast(forecast_data: Dict) -> List[str]:
    """
    Создание детального прогноза (по дням)
    
    Args:
        forecast_data (Dict): Данные прогноза
        
    Returns:
        List[str]: Список сообщений для каждого дня
    """
    if not forecast_data or not forecast_data.get('forecasts'):
        return ["❌ Данные прогноза недоступны"]
    
    messages = []
    forecasts = forecast_data.get('forecasts', [])
    
    for forecast in forecasts:
        date_obj = forecast.get('date', datetime.now())
        weather_emoji = get_weather_emoji(forecast.get('icon', ''))
        
        # Уровень комфорта
        comfort_level, comfort_desc = get_comfort_level(
            (forecast.get('temp_min', 0) + forecast.get('temp_max', 0)) / 2,
            forecast.get('avg_humidity', 0)
        )
        
        # Совет по погоде
        advice = get_weather_advice({
            'temperature': (forecast.get('temp_min', 0) + forecast.get('temp_max', 0)) / 2,
            'description': forecast.get('description', ''),
            'wind_speed': forecast.get('avg_wind_speed', 0),
            'humidity': forecast.get('avg_humidity', 0)
        })
        
        message = f"""
{weather_emoji} <b>{date_obj.strftime('%A, %d %B')}</b>

🌡️ <b>Температура:</b> {forecast.get('temp_min', 0)}° - {forecast.get('temp_max', 0)}°C
📝 <b>Описание:</b> {forecast.get('description', 'Неизвестно')}
💧 <b>Влажность:</b> {forecast.get('avg_humidity', 0)}%
💨 <b>Ветер:</b> {forecast.get('avg_wind_speed', 0)} м/с

{comfort_level} <b>Комфорт:</b> {comfort_desc}

💡 <b>Совет:</b> {advice}
"""
        
        messages.append(message.strip())
    
    return messages
