# ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБЩИХ УТИЛИТ
def parse_datetime(datetime_str: str) -> datetime:  # Парсинг даты в формате ISO
    try:
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))  # Преобразуем строку в datetime
    except ValueError:
        raise ValueError(f"Некорректный формат даты: {datetime_str}. Используйте ISO (YYYY-MM-DDTHH:MM:SS)")  # Ошибка
