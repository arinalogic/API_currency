# Модуль для сохранения и чтения данных в JSON-файл.
# Используется, чтобы хранить ответ API локально между запусками программы.

import json
import os
import time

# Сколько секунд кэш считается «свежим» (24 часа).
CACHE_MAX_AGE_SECONDS = 24 * 60 * 60


def save_to_file(data: dict, path: str = "currency_rate.json") -> None:
    """Сохраняет словарь в JSON-файл.

    data — данные для записи (например, ответ API с курсами валют).
    path — путь к файлу; по умолчанию currency_rate.json в текущей папке.
    Результат: файл на диске с читаемым JSON (отступы, кириллица без экранирования).
    """
    # Открываем файл на запись в кодировке UTF-8 (корректно для русских символов).
    with open(path, "w", encoding="utf-8") as file:
        # json.dump записывает словарь в файл; ensure_ascii=False — кириллица как есть,
        # indent=4 — отступы для удобного чтения человеком.
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_from_file(path: str = "currency_rate.json") -> dict:
    """Читает словарь из JSON-файла.

    path — путь к файлу; по умолчанию currency_rate.json.
    Возвращает dict с данными из файла.
    Если файла нет или JSON повреждён — Python выбросит стандартное исключение.
    """
    # Открываем файл на чтение в UTF-8 и разбираем JSON в словарь Python.
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def is_cache_valid(path: str = "currency_rate.json") -> bool:
    """Проверяет, можно ли использовать сохранённый файл как актуальный кэш.

    path — путь к JSON-файлу с курсами валют.
    Возвращает True, если файл есть и ему меньше 24 часов.
    Возвращает False, если файла нет или он старше 24 часов.
    """
    # Файла нет — кэша нет, нужен новый запрос к API.
    if not os.path.exists(path):
        return False

    # Время последнего изменения файла (Unix timestamp — секунды с 1970 года).
    file_modified_at = os.path.getmtime(path)

    # Сколько секунд прошло с момента сохранения файла.
    file_age_seconds = time.time() - file_modified_at

    # Файл свежий — меньше 24 часов; иначе кэш устарел.
    return file_age_seconds < CACHE_MAX_AGE_SECONDS
