#!/usr/bin/env python3
"""
Упрощенный скрипт для проверки работоспособности
"""

import os
import sys

# Проверяем наличие .env файла
if not os.path.exists('.env'):
    print("❌ Файл .env не найден!")
    print("📝 Создайте файл .env и добавьте:")
    print("BOT_TOKEN=ваш_telegram_bot_token")
    print("WEATHER_API_KEY=ваш_openweathermap_api_key")
    sys.exit(1)

# Проверяем наличие всех модулей
required_modules = ['config', 'weather_service', 'keyboards', 'utils', 'decorators']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
        print(f"✅ Модуль {module} найден")
    except ImportError as e:
        print(f"❌ Модуль {module} не найден: {e}")
        missing_modules.append(module)

if missing_modules:
    print(f"\n❌ Отсутствуют модули: {', '.join(missing_modules)}")
    print("Убедитесь, что все файлы созданы правильно.")
    sys.exit(1)

# Проверяем токены
try:
    from config import Config
    config = Config()
    print("✅ Конфигурация загружена")
    
    if config.validate_config():
        print("✅ Токены валидны")
    else:
        print("❌ Проблема с токенами в .env файле")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Ошибка конфигурации: {e}")
    sys.exit(1)

print("\n🚀 Все проверки пройдены! Запускаем бота...")

# Запускаем основной скрипт
try:
    from main import main
    import asyncio
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n👋 Бот остановлен пользователем")
except Exception as e:
    print(f"\n❌ Ошибка запуска: {e}")
    import traceback
    traceback.print_exc()
