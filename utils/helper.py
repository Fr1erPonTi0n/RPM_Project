# ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБЩИХ УТИЛИТ
import datetime

def parse_date(datetime_str: str) -> datetime.date:  # Парсинг даты в формате ISO
    try:
        return datetime.datetime.strptime(datetime_str, "%Y-%m-%d").date()  # Преобразуем строку в datetime
    except ValueError:
        raise ValueError(f"Некорректный формат даты: {datetime_str}. Используйте YYYY-MM-DD")  # Ошибка
