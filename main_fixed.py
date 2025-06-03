#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенная версия Telegram-бота для прогноза погоды
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from weather_service import WeatherService
from keyboards import get_main_keyboard
from utils import format_weather_message, format_forecast_message

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WeatherStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_forecast_city = State()


class WeatherBot:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(token=self.config.bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.weather_service = WeatherService(self.config.weather_api_key)
        self._setup_handlers()

    def _setup_handlers(self):
        """Регистрация обработчиков сообщений"""
        self.dp.message.register(self.start_handler, CommandStart())
        self.dp.message.register(self.help_handler, Command("help"))
        self.dp.message.register(self.weather_handler, Command("weather"))
        self.dp.message.register(self.forecast_handler, Command("forecast"))
        self.dp.message.register(
            self.process_city_weather, WeatherStates.waiting_for_city
        )
        self.dp.message.register(
            self.process_city_forecast, WeatherStates.waiting_for_forecast_city
        )

    async def start_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /start"""
        try:
            await state.clear()

            welcome_text = (
                "🌤️ <b>Добро пожаловать в Weather Bot!</b>\n\n"
                "Я помогу вам узнать актуальную погоду и прогноз для любого города мира.\n\n"
                "📍 <b>Доступные команды:</b>\n"
                "• /weather - текущая погода\n"
                "• /forecast - прогноз на 5 дней\n"
                "• /help - помощь\n\n"
                "Выберите действие из меню ниже:"
            )

            await message.answer(
                welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка в start_handler: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")

    async def help_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /help"""
        try:
            await state.clear()

            help_text = (
                "🆘 <b>Помощь по боту</b>\n\n"
                "🌡️ <b>/weather</b> - получить текущую погоду\n"
                "📅 <b>/forecast</b> - прогноз погоды на 5 дней\n\n"
                "💡 <b>Как пользоваться:</b>\n"
                "1. Выберите команду\n"
                "2. Введите название города\n"
                "3. Получите результат!\n\n"
                "🏙️ <b>Примеры городов:</b>\n"
                "• Москва\n"
                "• London\n"
                "• New York\n"
                "• Париж"
            )

            await message.answer(
                help_text, parse_mode="HTML", reply_markup=get_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка в help_handler: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")

    async def weather_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /weather"""
        try:
            await state.set_state(WeatherStates.waiting_for_city)

            await message.answer(
                "🏙️ <b>Текущая погода</b>\n\n"
                "Введите название города для получения актуальной информации о погоде:",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Ошибка в weather_handler: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")

    async def forecast_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /forecast"""
        try:
            await state.set_state(WeatherStates.waiting_for_forecast_city)

            await message.answer(
                "📅 <b>Прогноз погоды</b>\n\n"
                "Введите название города для получения прогноза на 5 дней:",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Ошибка в forecast_handler: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")

    async def process_city_weather(self, message: Message, state: FSMContext):
        """Обработка запроса текущей погоды"""
        try:
            city = message.text.strip()

            loading_msg = await message.answer("🔄 Получаю данные о погоде...")

            weather_data = await self.weather_service.get_current_weather(city)

            if weather_data:
                response_text = format_weather_message(weather_data)
                await loading_msg.edit_text(response_text, parse_mode="HTML")
            else:
                await loading_msg.edit_text(
                    f"❌ <b>Город '{city}' не найден</b>\n\n"
                    "Проверьте правильность написания и попробуйте снова.",
                    parse_mode="HTML",
                )

        except Exception as e:
            logger.error(f"Ошибка получения погоды: {e}")
            await message.answer(
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже или проверьте название города.",
                parse_mode="HTML",
            )

        await state.clear()

    async def process_city_forecast(self, message: Message, state: FSMContext):
        """Обработка запроса прогноза погоды"""
        try:
            city = message.text.strip()

            loading_msg = await message.answer("🔄 Получаю прогноз погоды...")

            forecast_data = await self.weather_service.get_forecast(city)

            if forecast_data:
                response_text = format_forecast_message(forecast_data)
                await loading_msg.edit_text(response_text, parse_mode="HTML")
            else:
                await loading_msg.edit_text(
                    f"❌ <b>Город '{city}' не найден</b>\n\n"
                    "Проверьте правильность написания и попробуйте снова.",
                    parse_mode="HTML",
                )

        except Exception as e:
            logger.error(f"Ошибка получения прогноза: {e}")
            await message.answer(
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже или проверьте название города.",
                parse_mode="HTML",
            )

        await state.clear()

    async def start_polling(self):
        """Запуск бота"""
        logger.info("Запуск Weather Bot...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            await self.bot.session.close()


async def main():
    """Главная функция"""
    bot = WeatherBot()
    await bot.start_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
