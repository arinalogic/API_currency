# Общий модуль HTTP-запросов для проекта API Explorer.
# Все GET-запросы в main.py и country_info.py идут через этот файл.

from typing import Any

import requests

# Таймаут по умолчанию: сколько секунд ждать ответ сервера.
DEFAULT_TIMEOUT = 10


def get(
    url: str,
    params: dict[str, Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    headers: dict[str, Any] | None = None,
) -> requests.Response | None:
    """Отправляет GET-запрос по URL.

    params  — query-параметры (?key=value), headers — заголовки запроса.
    При сетевой ошибке возвращает None (сервер недоступен, нет интернета и т.д.).
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.RequestException:
        return None

    return response


def is_ok(response: requests.Response) -> bool:
    """Базовая проверка статуса: True, если код ответа 2xx (успех)."""
    return response.ok
