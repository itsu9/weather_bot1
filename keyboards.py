#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль клавиатур для Telegram бота
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создание основной клавиатуры

    Returns:
        ReplyKeyboardMarkup: Основная клавиатура
    """
    builder = ReplyKeyboardBuilder()

    # Основные кнопки
    builder.add(
        KeyboardButton(text="🌡️ Текущая погода"),
        KeyboardButton(text="📅 Прогноз на 5 дней"),
    )

    # Дополнительные кнопки
    builder.add(
        KeyboardButton(text="📍 Избранные города"), KeyboardButton(text="⚙️ Настройки")
    )

    # Служебные кнопки
    builder.add(KeyboardButton(text="ℹ️ Помощь"), KeyboardButton(text="📊 О боте"))

    # Настройка размещения кнопок (2 в ряд)
    builder.adjust(2, 2, 2)

    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Выберите действие..."
    )


def get_weather_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для раздела текущей погоды

    Returns:
        ReplyKeyboardMarkup: Клавиатура погоды
    """
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(text="🔄 Обновить"), KeyboardButton(text="⭐ В избранное")
    )

    builder.add(KeyboardButton(text="📅 Прогноз"), KeyboardButton(text="🔙 Назад"))

    builder.adjust(2, 2)

    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Действия с погодой..."
    )


def get_forecast_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для раздела прогноза

    Returns:
        ReplyKeyboardMarkup: Клавиатура прогноза
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="🌡️ Сейчас"), KeyboardButton(text="📊 Подробно"))

    builder.add(KeyboardButton(text="⭐ В избранное"), KeyboardButton(text="🔙 В меню"))

    builder.adjust(2, 2)

    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Действия с прогнозом..."
    )


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура настроек

    Returns:
        ReplyKeyboardMarkup: Клавиатура настроек
    """
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(text="🌡️ Единицы измерения"), KeyboardButton(text="🌍 Язык")
    )

    builder.add(
        KeyboardButton(text="🔔 Уведомления"), KeyboardButton(text="📍 Местоположение")
    )

    builder.add(KeyboardButton(text="🔙 В главное меню"))

    builder.adjust(2, 2, 1)

    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Настройки бота..."
    )


def get_favorites_keyboard(cities: list = None) -> ReplyKeyboardMarkup:
    """
    Клавиатура избранных городов

    Args:
        cities (list): Список избранных городов

    Returns:
        ReplyKeyboardMarkup: Клавиатура избранных
    """
    builder = ReplyKeyboardBuilder()

    if cities:
        for city in cities[:6]:  # Максимум 6 городов
            builder.add(KeyboardButton(text=f"📍 {city}"))
    else:
        builder.add(KeyboardButton(text="➕ Добавить город"))

    builder.add(
        KeyboardButton(text="✏️ Редактировать"), KeyboardButton(text="🗑️ Очистить все")
    )

    builder.add(KeyboardButton(text="🔙 В главное меню"))

    # Настройка размещения
    if cities and len(cities) > 0:
        builder.adjust(2, 2, 1)
    else:
        builder.adjust(1, 2, 1)

    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Ваши избранные города..."
    )


def get_inline_weather_keyboard(city: str) -> InlineKeyboardMarkup:
    """
    Inline клавиатура для сообения с погодой

    Args:
        city (str): Название города

    Returns:
        InlineKeyboardMarkup: Inline клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="🔄 Обновить", callback_data=f"refresh_weather:{city}"
        )
    )

    builder.add(
        InlineKeyboardButton(text="📅 Прогноз", callback_data=f"get_forecast:{city}")
    )

    builder.add(
        InlineKeyboardButton(
            text="⭐ В избранное", callback_data=f"add_favorite:{city}"
        )
    )

    builder.add(
        InlineKeyboardButton(
            text="📤 Поделиться", switch_inline_query=f"Погода в {city}"
        )
    )

    builder.adjust(2, 2)

    return builder.as_markup()


def get_inline_forecast_keyboard(city: str) -> InlineKeyboardMarkup:
    """
    Inline клавиатура для прогноза

    Args:
        city (str): Название города

    Returns:
        InlineKeyboardMarkup: Inline клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="🌡️ Сейчас", callback_data=f"current_weather:{city}")
    )

    builder.add(
        InlineKeyboardButton(
            text="🔄 Обновить прогноз", callback_data=f"refresh_forecast:{city}"
        )
    )

    builder.add(
        InlineKeyboardButton(
            text="⭐ В избранное", callback_data=f"add_favorite:{city}"
        )
    )

    builder.add(
        InlineKeyboardButton(
            text="📤 Поделиться", switch_inline_query=f"Прогноз для {city}"
        )
    )

    builder.adjust(2, 2)

    return builder.as_markup()


def get_units_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора единиц измерения

    Returns:
        InlineKeyboardMarkup: Inline клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="🌡️ Цельсий (°C)", callback_data="units:metric")
    )

    builder.add(
        InlineKeyboardButton(text="🌡️ Фаренгейт (°F)", callback_data="units:imperial")
    )

    builder.add(
        InlineKeyboardButton(text="🌡️ Кельвин (K)", callback_data="units:kelvin")
    )

    builder.adjust(1)

    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка

    Returns:
        InlineKeyboardMarkup: Inline клавиатура
    """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"))

    builder.add(InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en"))

    builder.add(InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de"))

    builder.add(InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang:fr"))

    builder.adjust(2, 2)

    return builder.as_markup()
