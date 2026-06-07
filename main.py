# Консольное приложение для просмотра курсов валют.
# Связывает модули currency.py (запрос к API) и storage.py (кэш в файле).

from colorama import Fore, Style, init

from currency import CurrencyAPIError, get_currency_rates
from storage import is_cache_valid, read_from_file, save_to_file

# Валюты, которые показываем пользователю после загрузки данных.
DISPLAY_CURRENCIES = ("RUB", "EUR", "GBP")


def main() -> None:
    """Точка запуска программы: загрузка курсов, вывод данных и конвертер валют."""
    # Включаем цветной вывод в терминале Windows (сброс стиля после каждой строки).
    init(autoreset=True)

    # Спрашиваем у пользователя код базовой валюты (USD, EUR, RUB и т.д.).
    base = input("Введите код базовой валюты (например, USD): ").strip().upper()

    if not base:
        print(f"{Fore.RED}Ошибка: код валюты не может быть пустым.")
        return

    try:
        # Проверяем, есть ли свежий кэш (файл младше 24 часов).
        if is_cache_valid():
            data = read_from_file()

            # Кэш свежий, но мог быть сохранён для другой базовой валюты.
            if data.get("base_code") == base:
                print(f"{Fore.GREEN}Данные загружены из кэша")
            else:
                print(
                    f"{Fore.YELLOW}Кэш не подходит для выбранной валюты "
                    f"(в файле: {data.get('base_code')}, запрошено: {base})."
                )
                data = get_currency_rates(base)
                save_to_file(data)
                print(f"{Fore.CYAN}Данные получены из API")
        else:
            # Кэша нет или он устарел — запрашиваем актуальные курсы у API.
            data = get_currency_rates(base)
            save_to_file(data)
            print(f"{Fore.CYAN}Данные получены из API")

        # Извлекаем основные поля из ответа API (или из сохранённого JSON).
        base_code = data.get("base_code", "неизвестно")
        last_update = data.get("time_last_update_utc", "неизвестно")
        rates = data.get("rates", {})

        print(f"\n{Style.BRIGHT}Базовая валюта:{Style.RESET_ALL} {base_code}")
        print(f"{Style.BRIGHT}Дата последнего обновления:{Style.RESET_ALL} {last_update}")
        print(f"\n{Style.BRIGHT}Курсы:{Style.RESET_ALL}")

        # Выводим курсы для RUB, EUR и GBP относительно базовой валюты.
        for currency in DISPLAY_CURRENCIES:
            if currency in rates:
                print(f"  1 {base_code} = {Fore.GREEN}{rates[currency]}{Style.RESET_ALL} {currency}")
            else:
                print(f"  {Fore.YELLOW}Курс для {currency} не найден в ответе.")

        # --- Конвертер валют: перевод суммы из базовой валюты в выбранную ---
        print(f"\n{Style.BRIGHT}Конвертер валют:{Style.RESET_ALL}")

        target_currency = input(
            "Введите валюту назначения (например, RUB): "
        ).strip().upper()
        amount_input = input("Введите сумму для конвертации: ").strip()

        # Проверяем, что валюта назначения есть в словаре rates.
        if target_currency not in rates:
            print(
                f"{Fore.RED}Ошибка: валюта «{target_currency}» не найдена в списке курсов."
            )
            return

        # Преобразуем ввод в число; при ошибке завершаем программу без стектрейса.
        try:
            amount = float(amount_input)
        except ValueError:
            print(f"{Fore.RED}Ошибка: сумма должна быть числом (например, 100 или 99.5).")
            return

        # Курс показывает, сколько единиц target_currency за 1 единицу base_code.
        result = amount * rates[target_currency]

        print(
            f"\n{amount:g} {base_code} = "
            f"{Fore.GREEN}{result:.4f}{Style.RESET_ALL} {target_currency}"
        )

    except CurrencyAPIError as error:
        # Ошибки сети, неверный код ответа API и т.д. — показываем понятное сообщение.
        print(f"{Fore.RED}Ошибка при получении курсов: {error}")


if __name__ == "__main__":
    main()
