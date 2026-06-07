# Модуль для получения курсов валют через публичный API open.er-api.com.
# Здесь только логика запроса и разбора ответа — без CLI и сохранения в файл.

from http_client import get


class CurrencyAPIError(Exception):
    """Исключение при ошибке запроса курсов валют (сеть, неверный код ответа и т.д.)."""


def get_currency_rates(base: str) -> dict:
    """Запрашивает актуальные курсы валют относительно базовой валюты.

    base — код валюты в формате ISO (например, "USD", "EUR", "RUB").
    Возвращает словарь (dict) с полным ответом API, включая поле "rates".
    При любой ошибке выбрасывает CurrencyAPIError с понятным текстом.
    """
    base = base.upper()

    # Формируем URL: базовая валюта подставляется в конец адреса.
    url = f"https://open.er-api.com/v6/latest/{base}"

    # Отправляем GET-запрос через общий http_client (таймаут и обработка сети — там).
    response = get(url)

    # Если response is None — сеть недоступна, таймаут или другая ошибка requests.
    if response is None:
        raise CurrencyAPIError(
            f"Не удалось получить курсы для {base}: сервер недоступен или нет интернета."
        )

    # Успешный ответ API — только код 200.
    if response.status_code != 200:
        raise CurrencyAPIError(
            f"Не удалось получить курсы для {base}: "
            f"сервер вернул код {response.status_code}."
        )

    data = response.json()

    if data.get("result") != "success":
        raise CurrencyAPIError(
            f"API вернул ошибку для валюты {base}."
        )

    return data


# Локальный тест: запускается только при прямом вызове файла (python currency.py).
if __name__ == "__main__":
    test_base = "USD"
    print(f"Запрашиваем курсы валют с базой {test_base}...")

    try:
        data = get_currency_rates(test_base)
        print("Запрос успешен.")
        print(f"Базовая валюта: {data.get('base_code')}")
        print(f"Дата обновления: {data.get('time_last_update_utc')}")

        rates = data.get("rates", {})
        print(f"Количество валют в ответе: {len(rates)}")

        # Показываем несколько курсов для наглядности.
        for currency in ("EUR", "RUB", "GBP"):
            if currency in rates:
                print(f"  1 {test_base} = {rates[currency]} {currency}")

    except CurrencyAPIError as error:
        print(f"Ошибка: {error}")
