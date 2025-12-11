# ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ВАЛИДАЦИИ ВХОДНЫХ И ВЫХОДНЫХ ДАННЫХ ДЛЯ ДРУГИХ СКРИПТОВ

def validate_positive_int(value: int, name: str) -> None:  # Проверка, что число положительное целое
    if not isinstance(value, int) or value <= 0:  # Если значение не int или <= 0
        raise ValueError(f"{name} должен быть положительным целым числом, получено: {value}")  # Бросаем ошибку


def validate_status(status: str) -> None:  # Проверка допустимости статуса претензии
    valid_statuses = {"на рассмотрении", "решён", "не решён"}  # Набор допустимых статусов
    if status not in valid_statuses:  # Если статус не входит в допустимые
        raise ValueError(f"Недопустимый статус. Допустимые значения: {valid_statuses}")  # Бросаем ошибку


def validate_limit(limit: int) -> None:  # Проверка корректности лимита выборки
    if not isinstance(limit, int) or limit <= 0:  # Если лимит не int или <= 0
        raise ValueError(f"limit должен быть положительным целым числом, получено: {limit}")  # Бросаем ошибку
      

def validate_string(value: str, name: str, min_len: int = 1) -> None:  # Проверка строки
    if not isinstance(value, str) or len(value.strip()) < min_len:  # Если не строка или слишком короткая
        raise ValueError(f"{name} должно быть строкой длиной минимум {min_len} символов")  # Ошибка


def validate_price(value: float, name: str = "Цена") -> None:  # Проверка цены
    if not isinstance(value, (int, float)) or value <= 0:  # Если не число или <= 0
        raise ValueError(f"{name} должна быть положительным числом, получено: {value}")  # Ошибка


def validate_quantity(value: int, name: str = "Количество") -> None:  # Проверка количества
    if not isinstance(value, int) or value <= 0:  # Если не int или <= 0
        raise ValueError(f"{name} должно быть положительным целым числом, получено: {value}")  # Ошибка
