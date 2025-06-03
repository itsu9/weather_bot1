#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль конфигурации для Weather Bot
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    """Класс для управления конфигурацией бота"""
    
    def __init__(self):
        # Telegram Bot Token
        self.bot_token: str = self._get_env_var('BOT_TOKEN')
        
        # OpenWeatherMap API Key
        self.weather_api_key: str = self._get_env_var('WEATHER_API_KEY')
        
        # API URLs
        self.weather_base_url: str = 'https://api.openweathermap.org/data/2.5'
        self.current_weather_url: str = f'{self.weather_base_url}/weather'
        self.forecast_url: str = f'{self.weather_base_url}/forecast'
        
        # Настройки запросов
        self.request_timeout: int = 10
        self.max_retries: int = 3
        
        # Языковые настройки
        self.default_language: str = 'ru'
        self.default_units: str = 'metric'
        
        # Настройки кэширования (если нужно добавить в будущем)
        self.cache_ttl: int = 300  # 5 минут
        
    def _get_env_var(self, var_name: str) -> str:
        """
        Получение переменной окружения с проверкой
        
        Args:
            var_name (str): Название переменной
            
        Returns:
            str: Значение переменной
            
        Raises:
            ValueError: Если переменная не найдена
        """
        value = os.getenv(var_name)
        if not value:
            raise ValueError(
                f"Переменная окружения {var_name} не найдена!\n"
                f"Создайте файл .env или установите переменную окружения."
            )
        return value
    
    def validate_config(self) -> bool:
        """
        Проверка корректности конфигурации
        
        Returns:
            bool: True если конфигурация валидна
        """
        try:
            # Проверяем наличие основных параметров
            if not self.bot_token or len(self.bot_token) < 10:
                return False
                
            if not self.weather_api_key or len(self.weather_api_key) < 10:
                return False
                
            return True
            
        except Exception:
            return False
    
    def get_weather_params(self, city: str, forecast: bool = False) -> dict:
        """
        Получение параметров для API запроса
        
        Args:
            city (str): Название города
            forecast (bool): Прогноз или текущая погода
            
        Returns:
            dict: Словарь параметров
        """
        params = {
            'q': city,
            'appid': self.weather_api_key,
            'lang': self.default_language,
            'units': self.default_units
        }
        
        if forecast:
            params['cnt'] = 40  # 5 дней по 3-часовым интервалам
            
        return params


# Глобальная конфигурация (синглтон)
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Получение экземпляра конфигурации (синглтон)
    
    Returns:
        Config: Экземпляр конфигурации
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance 
