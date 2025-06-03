#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный модуль Telegram-бота для прогноза погоды с полной поддержкой кнопок
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from weather_service import WeatherService
from keyboards import (
    get_main_keyboard, 
    get_forecast_keyboard, 
    get_settings_keyboard,
    get_favorites_keyboard,
    get_inline_weather_keyboard,
    get_inline_forecast_keyboard,
    get_units_keyboard,
    get_language_keyboard
)
from utils import format_weather_message, format_forecast_message
from decorators import error_handler


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_forecast_city = State()
    waiting_for_favorite_city = State()


class WeatherBot:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(token=self.config.bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.weather_service = WeatherService(self.config.weather_api_key)
        
        # Простое хранилище избранных городов (в реальном проекте - база данных)
        self.user_favorites = {}
        
        self._setup_handlers()

    def _setup_handlers(self):
        """Регистрация обработчиков сообщений"""
        # Команды
        self.dp.message.register(self.start_handler, CommandStart())
        self.dp.message.register(self.help_handler, Command("help"))
        self.dp.message.register(self.weather_handler, Command("weather"))
        self.dp.message.register(self.forecast_handler, Command("forecast"))
        
        # Кнопки главного меню
        self.dp.message.register(self.menu_current_weather, F.text == "🌡️ Текущая погода")
        self.dp.message.register(self.menu_forecast, F.text == "📅 Прогноз на 5 дней")
        self.dp.message.register(self.menu_favorites, F.text == "📍 Избранные города")
        self.dp.message.register(self.menu_settings, F.text == "⚙️ Настройки")
        self.dp.message.register(self.menu_help, F.text == "ℹ️ Помощь")
        self.dp.message.register(self.menu_about, F.text == "📊 О боте")
        
        # Кнопки возврата
        self.dp.message.register(self.back_to_menu, F.text.in_(["🔙 В главное меню", "🔙 В меню", "🔙 Назад"]))
        
        # Кнопки избранного
        self.dp.message.register(self.add_favorite_city, F.text == "➕ Добавить город")
        self.dp.message.register(self.clear_favorites, F.text == "🗑️ Очистить все")
        
        # Обработка избранных городов (начинающихся с 📍)
        self.dp.message.register(self.handle_favorite_city, F.text.startswith("📍 "))
        
        # Состояния ввода
        self.dp.message.register(self.process_city_weather, WeatherStates.waiting_for_city)
        self.dp.message.register(self.process_city_forecast, WeatherStates.waiting_for_forecast_city)
        self.dp.message.register(self.process_add_favorite, WeatherStates.waiting_for_favorite_city)
        
        # Inline кнопки (callback queries)
        self.dp.callback_query.register(self.handle_callback)

    @error_handler
    async def start_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /start"""
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
            welcome_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )

    @error_handler
    async def help_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /help"""
        await state.clear()
        await self._send_help(message)

    @error_handler
    async def menu_help(self, message: Message, state: FSMContext):
        """Обработчик кнопки помощи"""
        await state.clear()
        await self._send_help(message)

    async def _send_help(self, message: Message):
        """Отправка справки"""
        help_text = (
            "🆘 <b>Помощь по боту</b>\n\n"
            "🌡️ <b>Текущая погода</b> - получить актуальную погоду для города\n"
            "📅 <b>Прогноз на 5 дней</b> - подробный прогноз погоды\n"
            "📍 <b>Избранные города</b> - сохраните часто используемые города\n"
            "⚙️ <b>Настройки</b> - настройка единиц измерения и языка\n\n"
            "💡 <b>Как пользоваться:</b>\n"
            "1. Нажмите нужную кнопку в меню\n"
            "2. Введите название города\n"
            "3. Получите результат!\n\n"
            "🏙️ <b>Примеры городов:</b>\n"
            "• Москва, Санкт-Петербург\n"
            "• London, New York\n"
            "• Париж, Берлин\n\n"
            "Бот поддерживает города на русском и английском языках."
        )
        
        await message.answer(
            help_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )

    @error_handler
    async def menu_about(self, message: Message, state: FSMContext):
        """Обработчик кнопки 'О боте'"""
        await state.clear()
        
        about_text = (
            "📊 <b>О Weather Bot</b>\n\n"
            "🤖 <b>Версия:</b> 1.0.0\n"
            "📅 <b>Дата создания:</b> Июнь 2025\n"
            "🌍 <b>API:</b> OpenWeatherMap\n"
            "⚡ <b>Технологии:</b> aiogram 3.x, Python 3.9+\n\n"
            "✨ <b>Возможности:</b>\n"
            "• Текущая погода для любого города\n"
            "• Прогноз на 5 дней с 3-часовым интервалом\n"
            "• Сохранение избранных городов\n"
            "• Настройка единиц измерения\n"
            "• Многоязычная поддержка\n\n"
            "🔄 <b>Обновления погоды:</b> в реальном времени\n"
            "📊 <b>Данные предоставлены:</b> OpenWeatherMap\n\n"
            "💬 Бот работает 24/7 и готов помочь вам с прогнозом погоды!"
        )
        
        await message.answer(
            about_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )

    @error_handler
    async def weather_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /weather"""
        await self._request_city_for_weather(message, state)

    @error_handler
    async def menu_current_weather(self, message: Message, state: FSMContext):
        """Обработчик кнопки 'Текущая погода'"""
        await self._request_city_for_weather(message, state)

    async def _request_city_for_weather(self, message: Message, state: FSMContext):
        """Запрос города для получения текущей погоды"""
        await state.set_state(WeatherStates.waiting_for_city)
        
        await message.answer(
            "🏙️ <b>Текущая погода</b>\n\n"
            "Введите название города для получения актуальной информации о погоде:",
            parse_mode='HTML'
        )

    @error_handler
    async def forecast_handler(self, message: Message, state: FSMContext):
        """Обработчик команды /forecast"""
        await self._request_city_for_forecast(message, state)

    @error_handler
    async def menu_forecast(self, message: Message, state: FSMContext):
        """Обработчик кнопки 'Прогноз на 5 дней'"""
        await self._request_city_for_forecast(message, state)

    async def _request_city_for_forecast(self, message: Message, state: FSMContext):
        """Запрос города для получения прогноза"""
        await state.set_state(WeatherStates.waiting_for_forecast_city)
        
        await message.answer(
            "📅 <b>Прогноз погоды</b>\n\n"
            "Введите название города для получения прогноза на 5 дней:",
            parse_mode='HTML'
        )

    @error_handler
    async def menu_favorites(self, message: Message, state: FSMContext):
        """Обработчик кнопки 'Избранные города'"""
        await state.clear()
        
        user_id = message.from_user.id
        favorites = self.user_favorites.get(user_id, [])
        
        if favorites:
            text = (
                "📍 <b>Ваши избранные города:</b>\n\n"
                f"Всего сохранено: {len(favorites)} городов\n\n"
                "Нажмите на город для получения погоды или выберите действие:"
            )
        else:
            text = (
                "📍 <b>Избранные города</b>\n\n"
                "У вас пока нет сохраненных городов.\n"
                "Добавьте город, чтобы быстро получать прогноз погоды!"
            )
        
        await message.answer(
            text,
            parse_mode='HTML',
            reply_markup=get_favorites_keyboard(favorites)
        )

    @error_handler
    async def add_favorite_city(self, message: Message, state: FSMContext):
        """Обработчик кнопки 'Добавить город'"""
        await state.set_state(WeatherStates.waiting_for_favorite_city)
        
        await message.answer(
            "🏙️ <b>Добавление города в избранное</b>\n\n"
            "Введите название города, который хотите добавить в избранное:",
            parse_mode='HTML'
        )

    @error_handler
    async def process_add_favorite(self, message: Message, state: FSMContext):
        """Обработка добавления города в избранное"""
        city = message.text.strip()
        user_id = message.from_user.id
        
        # Проверяем, существует ли город (запрашиваем погоду)
        loading_msg = await message.answer("🔄 Проверяю город...")
        
        try:
            weather_data = await self.weather_service.get_current_weather(city)
            
            if weather_data:
                # Город найден, добавляем в избранное
                if user_id not in self.user_favorites:
                    self.user_favorites[user_id] = []
                
                favorites = self.user_favorites[user_id]
                
                # Проверяем, нет ли уже такого города
                city_name = weather_data.get('name', city)
                if city_name not in favorites:
                    if len(favorites) < 6:  # Ограничение на количество
                        favorites.append(city_name)
                        await loading_msg.edit_text(
                            f"✅ <b>Город '{city_name}' добавлен в избранное!</b>\n\n"
                            f"Всего избранных городов: {len(favorites)}",
                            parse_mode='HTML'
                        )
                    else:
                        await loading_msg.edit_text(
                            "❌ <b>Превышен лимит</b>\n\n"
                            "Можно сохранить максимум 6 городов. "
                            "Удалите один из существующих городов.",
                            parse_mode='HTML'
                        )
                else:
                    await loading_msg.edit_text(
                        f"ℹ️ <b>Город '{city_name}' уже в избранном</b>",
                        parse_mode='HTML'
                    )
                
                # Показываем обновленный список избранного
                await asyncio.sleep(2)
                await message.answer(
                    "📍 Ваши избранные города:",
                    reply_markup=get_favorites_keyboard(self.user_favorites[user_id])
                )
                
            else:
                await loading_msg.edit_text(
                    f"❌ <b>Город '{city}' не найден</b>\n\n"
                    "Проверьте правильность написания и попробуйте снова.",
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка добавления города в избранное: {e}")
            await loading_msg.edit_text(
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже.",
                parse_mode='HTML'
            )
        
        await state.clear()

    @error_handler
    async def handle_favorite_city(self, message: Message, state: FSMContext):
        """Обработка нажатия на избранный город"""
        await state.clear()
        
        # Извлекаем название города (убираем 📍 и пробел)
        city = message.text[2:].strip()
        
        loading_msg = await message.answer("🔄 Получаю данные о погоде...")
        
        try:
            weather_data = await self.weather_service.get_current_weather(city)
            
            if weather_data:
                response_text = format_weather_message(weather_data)
                await loading_msg.edit_text(
                    response_text,
                    parse_mode='HTML',
                    reply_markup=get_inline_weather_keyboard(city)
                )
            else:
                await loading_msg.edit_text(
                    f"❌ <b>Не удалось получить погоду для '{city}'</b>",
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка получения погоды для избранного города {city}: {e}")
            await loading_msg.edit_text(
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже.",
                parse_mode='HTML'
            )

    @error_handler
    async def clear_favorites(self, message: Message, state: FSMContext):
        """Очистка избранных городов"""
        await state.clear()
        
        user_id = message.from_user.id
        
        if user_id in self.user_favorites:
            del self.user_favorites[user_id]
        
        await message.answer(
            "🗑️ <b>Избранные города очищены</b>\n\n"
            "Все сохраненные города удалены.",
            parse_mode='HTML',
            reply_markup=get_favorites_keyboard([])
        )

    @error_handler
    async def menu_settings(self, message: Message, state: FSMContext):
        """Обработчик кнопки 'Настройки'"""
        await state.clear()
        
        settings_text = (
            "⚙️ <b>Настройки бота</b>\n\n"
            "Здесь вы можете настроить работу бота под себя:\n\n"
            "🌡️ <b>Единицы измерения</b> - Цельсий, Фаренгейт или Кельвин\n"
            "🌍 <b>Язык</b> - язык интерфейса и данных\n"
            "🔔 <b>Уведомления</b> - настройка push-уведомлений\n"
            "📍 <b>Местоположение</b> - автоопределение города\n\n"
            "Выберите раздел для настройки:"
        )
        
        await message.answer(
            settings_text,
            parse_mode='HTML',
            reply_markup=get_settings_keyboard()
        )

    @error_handler
    async def back_to_menu(self, message: Message, state: FSMContext):
        """Возврат в главное меню"""
        await state.clear()
        
        await message.answer(
            "🏠 <b>Главное меню</b>\n\n"
            "Выберите действие:",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )

    @error_handler
    async def process_city_weather(self, message: Message, state: FSMContext):
        """Обработка запроса текущей погоды"""
        city = message.text.strip()
        
        loading_msg = await message.answer("🔄 Получаю данные о погоде...")
        
        try:
            weather_data = await self.weather_service.get_current_weather(city)
            
            if weather_data:
                response_text = format_weather_message(weather_data)
                await loading_msg.edit_text(
                    response_text,
                    parse_mode='HTML',
                    reply_markup=get_inline_weather_keyboard(city)
                )
                
                # Показываем главное меню
                await message.answer(
                    "Выберите действие:",
                    reply_markup=get_main_keyboard()
                )
            else:
                await loading_msg.edit_text(
                    f"❌ <b>Город '{city}' не найден</b>\n\n"
                    "Проверьте правильность написания и попробуйте снова.",
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка получения погоды для {city}: {e}")
            await loading_msg.edit_text(
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже или проверьте название города.",
                parse_mode='HTML'
            )
        
        await state.clear()

    @error_handler
    async def process_city_forecast(self, message: Message, state: FSMContext):
        """Обработка запроса прогноза погоды"""
        city = message.text.strip()
        
        loading_msg = await message.answer("🔄 Получаю прогноз погоды...")
        
        try:
            forecast_data = await self.weather_service.get_forecast(city)
            
            if forecast_data:
                response_text = format_forecast_message(forecast_data)
                await loading_msg.edit_text(
                    response_text,
                    parse_mode='HTML',
                    reply_markup=get_inline_forecast_keyboard(city)
                )
                
                # Показываем меню прогноза
                await message.answer(
                    "Выберите действие:",
                    reply_markup=get_forecast_keyboard()
                )
            else:
                await loading_msg.edit_text(
                    f"❌ <b>Город '{city}' не найден</b>\n\n"
                    "Проверьте правильность написания и попробуйте снова.",
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка получения прогноза для {city}: {e}")
            await loading_msg.edit_text(
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже или проверьте название города.",
                parse_mode='HTML'
            )
        
        await state.clear()

    @error_handler
    async def handle_callback(self, callback: CallbackQuery, state: FSMContext):
        """Обработка inline кнопок"""
        data = callback.data
        
        try:
            if data.startswith("refresh_weather:"):
                city = data.split(":", 1)[1]
                weather_data = await self.weather_service.get_current_weather(city)
                
                if weather_data:
                    response_text = format_weather_message(weather_data)
                    await callback.message.edit_text(
                        response_text,
                        parse_mode='HTML',
                        reply_markup=get_inline_weather_keyboard(city)
                    )
                    await callback.answer("🔄 Погода обновлена!")
                else:
                    await callback.answer("❌ Ошибка обновления данных", show_alert=True)
                    
            elif data.startswith("refresh_forecast:"):
                city = data.split(":", 1)[1]
                forecast_data = await self.weather_service.get_forecast(city)
                
                if forecast_data:
                    response_text = format_forecast_message(forecast_data)
                    await callback.message.edit_text(
                        response_text,
                        parse_mode='HTML',
                        reply_markup=get_inline_forecast_keyboard(city)
                    )
                    await callback.answer("🔄 Прогноз обновлен!")
                else:
                    await callback.answer("❌ Ошибка обновления прогноза", show_alert=True)
                    
            elif data.startswith("get_forecast:"):
                city = data.split(":", 1)[1]
                forecast_data = await self.weather_service.get_forecast(city)
                
                if forecast_data:
                    response_text = format_forecast_message(forecast_data)
                    await callback.message.answer(
                        response_text,
                        parse_mode='HTML',
                        reply_markup=get_inline_forecast_keyboard(city)
                    )
                    await callback.answer()
                else:
                    await callback.answer("❌ Ошибка получения прогноза", show_alert=True)
                    
            elif data.startswith("current_weather:"):
                city = data.split(":", 1)[1]
                weather_data = await self.weather_service.get_current_weather(city)
                
                if weather_data:
                    response_text = format_weather_message(weather_data)
                    await callback.message.answer(
                        response_text,
                        parse_mode='HTML',
                        reply_markup=get_inline_weather_keyboard(city)
                    )
                    await callback.answer()
                else:
                    await callback.answer("❌ Ошибка получения погоды", show_alert=True)
                    
            elif data.startswith("add_favorite:"):
                city = data.split(":", 1)[1]
                user_id = callback.from_user.id
                
                if user_id not in self.user_favorites:
                    self.user_favorites[user_id] = []
                
                favorites = self.user_favorites[user_id]
                
                if city not in favorites:
                    if len(favorites) < 6:
                        favorites.append(city)
                        await callback.answer(f"⭐ {city} добавлен в избранное!")
                    else:
                        await callback.answer("❌ Превышен лимит избранных городов (6)", show_alert=True)
                else:
                    await callback.answer(f"ℹ️ {city} уже в избранном")
                    
            elif data.startswith("units:"):
                unit = data.split(":", 1)[1]
                await callback.answer(f"🌡️ Единицы измерения: {unit}")
                
            elif data.startswith("lang:"):
                lang = data.split(":", 1)[1]
                await callback.answer(f"🌍 Язык изменен на: {lang}")
                
            else:
                await callback.answer("🤖 Функция в разработке")
                
        except Exception as e:
            logger.error(f"Ошибка обработки callback {data}: {e}")
            await callback.answer("❌ Произошла ошибка", show_alert=True)

    async def start_polling(self):
        """Запуск бота"""
        logger.info("Запуск Weather Bot с полной поддержкой кнопок...")
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


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
