#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Декораторы для обработки ошибок и логирования
"""

import logging
import functools
from typing import Callable, Any
from aiogram.types import Message

logger = logging.getLogger(__name__)


def error_handler(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок в хэндлерах
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {e}")

            # Находим объект message
            message = None
            for arg in args:
                if isinstance(arg, Message):
                    message = arg
                    break

            if message:
                try:
                    await message.answer(
                        "⚠️ <b>Произошла ошибка</b>\n\n"
                        "Попробуйте повторить запрос позже.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

    return wrapper
