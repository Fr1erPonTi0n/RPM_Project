# ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБЩИХ УТИЛИТ
import datetime

def parse_date(datetime_str: str) -> datetime.date:
    """Парсинг даты и времени в формате ISO"""
    formats = [
        "%Y-%m-%d %H:%M",  # 2025-12-15 20:45
        "%Y-%m-%d",  # 2025-12-15
        "%d.%m.%Y %H:%M",  # 15.12.2025 20:45
        "%d.%m.%Y"  # 15.12.2025
    ]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(datetime_str, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Некорректный формат даты/времени: {datetime_str}. Используйте YYYY-MM-DD HH:MM или YYYY-MM-DD")