from sqlalchemy.orm import Session  # Импортируем класс Session из SQLAlchemy — нужен для работы с базой данных
from sqlalchemy import and_, or_  # Импортируем функции: and_, or_ (логические операторы для фильтров)
from datetime import date, timedelta  # Импортируем классы для работы с датами: date и timedelta
from typing import List, Optional, Dict, Any  # Импортируем типы для аннотаций: список, опциональные значения, словари
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.license import Contract, License  # Импортируем ORM-модели Contract и License из модуля license
from utils.validators import validate_positive_int, validate_string
from utils.helper import parse_date

######################### создание заказа 
def create_contract(db: Session, supplier_id: int, title: str,
                    start_date_str: str, end_date_str: str, file_path: Optional[str] = None) -> Contract:  # Функция для создания нового контракта
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем, что ID поставщика — положительное целое число
    validate_string(title, "Название контракта", min_len=3)  # Проверяем, что название контракта — строка длиной минимум 3 символа

    start_date = parse_date(start_date_str)  # Преобразуем строку даты начала в объект date
    end_date = parse_date(end_date_str)  # Преобразуем строку даты окончания в объект date

    if start_date > end_date:  # Если дата начала позже даты окончания
        raise ValueError("Дата начала контракта не может быть позже даты окончания")  # Ошибка
    if end_date < date.today():  # Если дата окончания уже прошла
        raise ValueError("Дата окончания контракта не может быть в прошлом")  # Ошибка

    new_contract = Contract(  # Создаём объект контракта
        supplier_id=supplier_id,  # ID поставщика
        title=title.strip(),  # Название контракта (убираем пробелы)
        start_date=start_date,  # Дата начала
        end_date=end_date,  # Дата окончания
        file_path=file_path.strip() if file_path else None  # Путь к файлу (если указан)
    )

    db.add(new_contract)
    db.commit()  # Добавляем контракт в сессию
    db.refresh(new_contract)  # Обновляем объект, чтобы получить актуальные данные из базы
    return new_contract  # Возвращаем созданный контракт


def get_all_contracts(db: Session, supplier_id: Optional[int] = None,
                      active_only: bool = False) -> List[Contract]:  # Получить список контрактов
    query = db.query(Contract)  # Базовый запрос ко всем контрактам
    if supplier_id is not None:  # Если указан фильтр по поставщику
        validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID
        query = query.filter(Contract.supplier_id == supplier_id)  # Фильтруем по поставщику
    if active_only:  # Если нужны только активные контракты
        today = date.today()  # Сегодняшняя дата
        query = query.filter(Contract.start_date <= today, Contract.end_date >= today)  # Фильтруем по активным
    return query.order_by(Contract.end_date.desc()).all()  # Сортируем по дате окончания и возвращаем список


def get_contract_by_id(db: Session, contract_id: int) -> Optional[Contract]:  # Получить контракт по ID
    validate_positive_int(contract_id, "ID контракта")  # Проверяем ID
    return db.query(Contract).filter(Contract.id == contract_id).first()  # Ищем контракт по ID


def update_contract(db: Session, contract_id: int, title: Optional[str] = None,
                    end_date_str: Optional[str] = None, file_path: Optional[str] = None) -> Optional[Contract]:  # Обновить контракт
    validate_positive_int(contract_id, "ID контракта")  # Проверяем ID
    contract = db.query(Contract).filter(Contract.id == contract_id).first()  # Ищем контракт
    if not contract:  # Если контракт не найден
        return None  # Возвращаем None

    if title is not None:  # Если нужно обновить название
        validate_string(title, "Название контракта", min_len=3)  # Проверяем строку
        contract.title = title.strip()  # Обновляем название

    if end_date_str is not None:  # Если нужно обновить дату окончания
        new_end_date = parse_date(end_date_str)  # Парсим дату
        if new_end_date < contract.start_date:  # Проверка: дата окончания раньше даты начала
            raise ValueError("Дата окончания контракта не может быть раньше даты начала")
        if new_end_date < date.today():  # Проверка: дата окончания в прошлом
            raise ValueError("Дата окончания контракта не может быть в прошлом")
        contract.end_date = new_end_date  # Обновляем дату окончания

    if file_path is not None:  # Если нужно обновить путь к файлу
        contract.file_path = file_path.strip() if file_path else None  # Обновляем путь

    db.add(contract)
    db.commit()
    db.refresh(contract)  # Обновляем объект
    return contract  # Возвращаем обновлённый контракт


def delete_contract(db: Session, contract_id: int) -> bool:  # Удалить контракт
    validate_positive_int(contract_id, "ID контракта")  # Проверяем ID
    contract = db.query(Contract).filter(Contract.id == contract_id).first()  # Ищем контракт
    if not contract:  # Если контракт не найден
        return False  # Возвращаем False

    license_count = db.query(License).filter(License.contract_id == contract_id).count()  # Считаем связанные лицензии
    if license_count > 0:  # Если есть связанные лицензии
        raise ValueError(f"Невозможно удалить контракт: есть {license_count} связанных лицензий")  # Ошибка

    with db.begin():  # Транзакция
        db.delete(contract)  # Удаляем контракт
    return True  # Возвращаем True (успех)

def create_license(db: Session, supplier_id: int, contract_id: int, film_title: str,
                   digital_key: str, start_date_str: str, end_date_str: str) -> License:  # Функция для создания новой лицензии
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем, что ID поставщика — положительное целое число
    validate_positive_int(contract_id, "ID контракта")  # Проверяем, что ID контракта — положительное целое число
    validate_string(film_title, "Название фильма", min_len=1)  # Проверяем, что название фильма — непустая строка
    validate_string(digital_key, "Цифровой ключ", min_len=1)  # Проверяем, что цифровой ключ — непустая строка

    start_date = parse_date(start_date_str)  # Преобразуем строку даты начала в объект date
    end_date = parse_date(end_date_str)  # Преобразуем строку даты окончания в объект date

    if start_date > end_date:  # Если дата начала позже даты окончания
        raise ValueError("Дата начала лицензии не может быть позже даты окончания")  # Ошибка
    if end_date < date.today():  # Если дата окончания уже прошла
        raise ValueError("Дата окончания лицензии не может быть в прошлом")  # Ошибка

    contract = db.query(Contract).filter(Contract.id == contract_id).first()  # Ищем контракт по ID
    if not contract:  # Если контракт не найден
        raise ValueError(f"Контракт с ID {contract_id} не найден")  # Ошибка

    if start_date < contract.start_date or end_date > contract.end_date:  # Проверяем, что лицензия в пределах контракта
        raise ValueError("Период действия лицензии должен быть в пределах действия контракта")  # Ошибка

    existing_license = db.query(License).filter(  # Проверяем, нет ли уже лицензии на этот фильм или ключ
        and_(
            License.film_title.ilike(film_title.strip()),  # Сравниваем название фильма без учёта регистра
            or_(
                and_(License.start_date <= end_date, License.end_date >= start_date),  # Пересечение по датам
                License.digital_key == digital_key.strip()  # Или совпадение цифрового ключа
            )
        )
    ).first()
    if existing_license:  # Если нашли совпадение
        raise ValueError(f"Лицензия на фильм '{film_title}' уже существует или ключ занят")  # Ошибка

    new_license = License(  # Создаём объект лицензии
        supplier_id=supplier_id,  # ID поставщика
        contract_id=contract_id,  # ID контракта
        film_title=film_title.strip(),  # Название фильма (убираем пробелы)
        digital_key=digital_key.strip(),  # Цифровой ключ (убираем пробелы)
        start_date=start_date,  # Дата начала
        end_date=end_date  # Дата окончания
    )

    db.add(new_license)
    db.commit() # Добавляем лицензию в базу
    db.refresh(new_license)  # Обновляем объект
    return new_license  # Возвращаем созданную лицензию


def get_all_licenses(db: Session, supplier_id: Optional[int] = None,
                     contract_id: Optional[int] = None, active_only: bool = False) -> List[License]:  # Получить список лицензий
    query = db.query(License)  # Базовый запрос ко всем лицензиям
    if supplier_id is not None:  # Если указан фильтр по поставщику
        validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID
        query = query.filter(License.supplier_id == supplier_id)  # Фильтруем по поставщику
    if contract_id is not None:  # Если указан фильтр по контракту
        validate_positive_int(contract_id, "ID контракта")  # Проверяем ID
        query = query.filter(License.contract_id == contract_id)  # Фильтруем по контракту
    if active_only:  # Если нужны только активные лицензии
        today = date.today()  # Сегодняшняя дата
        query = query.filter(License.start_date <= today, License.end_date >= today)  # Фильтруем по активным
    return query.order_by(License.end_date.desc()).all()  # Сортируем по дате окончания и возвращаем список


def get_license_by_id(db: Session, license_id: int) -> Optional[License]:  # Получить лицензию по ID
    validate_positive_int(license_id, "ID лицензии")  # Проверяем ID
    return db.query(License).filter(License.id == license_id).first()  # Ищем лицензию по ID


def update_license(db: Session, license_id: int, film_title: Optional[str] = None,
                   digital_key: Optional[str] = None, end_date_str: Optional[str] = None) -> Optional[License]:  # Обновить лицензию
    validate_positive_int(license_id, "ID лицензии")  # Проверяем ID
    license_obj = db.query(License).filter(License.id == license_id).first()  # Ищем лицензию
    if not license_obj:  # Если лицензия не найдена
        return None  # Возвращаем None

    if film_title is not None:  # Если нужно обновить название фильма
        validate_string(film_title, "Название фильма", min_len=1)  # Проверяем строку
        license_obj.film_title = film_title.strip()  # Обновляем название

    if digital_key is not None:  # Если нужно обновить цифровой ключ
        validate_string(digital_key, "Цифровой ключ", min_len=1)  # Проверяем строку
        existing = db.query(License).filter(License.digital_key == digital_key.strip(),
                                            License.id != license_id).first()  # Проверяем, не занят ли ключ другой лицензией
        if existing:  # Если ключ занят
            raise ValueError(f"Цифровой ключ '{digital_key}' уже используется")  # Ошибка
        license_obj.digital_key = digital_key.strip()  # Обновляем ключ

    if end_date_str is not None:  # Если нужно обновить дату окончания
        new_end_date = parse_date(end_date_str)  # Парсим дату
        if new_end_date < license_obj.start_date:  # Проверка: дата окончания раньше даты начала
            raise ValueError("Дата окончания лицензии не может быть раньше даты начала")
        if new_end_date < date.today():  # Проверка: дата окончания в прошлом
            raise ValueError("Дата окончания лицензии не может быть в прошлом")
        contract = db.query(Contract).filter(Contract.id == license_obj.contract_id).first()  # Проверяем контракт
        if contract and new_end_date > contract.end_date:  # Проверка: дата окончания позже контракта
            raise ValueError("Дата окончания лицензии не может быть позже окончания контракта")
        license_obj.end_date = new_end_date  # Обновляем дату окончания

    with db.begin():  # Транзакция
        db.add(license_obj)  # Сохраняем изменения
    db.refresh(license_obj)  # Обновляем объект
    return license_obj  # Возвращаем обновлённую лицензию


def delete_license(db: Session, license_id: int) -> bool:  # Удалить лицензию
    validate_positive_int(license_id, "ID лицензии")  # Проверяем ID
    license_obj = db.query(License).filter(License.id == license_id).first()  # Ищем лицензию
    if not license_obj:  # Если лицензия не найдена
        return False  # Возвращаем False

    from models.cinema import Film  # Импортируем модель Film для проверки связей
    film_exists = db.query(Film).filter(Film.license_id == license_id).first()  # Проверяем, есть ли фильм с этой лицензией
    if film_exists:  # Если фильм найден
        raise ValueError(f"Невозможно удалить лицензию: есть связанный фильм (ID: {film_exists.id})")  # Ошибка

    db.delete(license_obj)
    db.commit()
    return True  # Возвращаем True (успех)

# АНАЛИТИКА КОНТРАКТОВ И ЛИЦЕНЗИЙ

def get_expiring_contracts(db: Session, days_threshold: int = 30) -> List[Dict[str, Any]]:  # Получить контракты, срок которых скоро истекает
    validate_positive_int(days_threshold, "Пороговое значение дней")  # Проверяем, что порог — положительное число
    today = date.today()  # Получаем сегодняшнюю дату
    threshold_date = today + timedelta(days=days_threshold)  # Вычисляем дату порога (сегодня + days_threshold)

    expiring_contracts = db.query(Contract).filter(  # Запрашиваем контракты из базы
        Contract.end_date >= today,  # Дата окончания должна быть не раньше сегодняшней
        Contract.end_date <= threshold_date  # И не позже пороговой даты
    ).order_by(Contract.end_date).all()  # Сортируем по дате окончания и получаем список

    result = []  # Список для хранения результатов
    for contract in expiring_contracts:  # Перебираем найденные контракты
        result.append({
            'contract_id': contract.id,  # ID контракта
            'title': contract.title,  # Название контракта
            'supplier_id': contract.supplier_id,  # ID поставщика
            'end_date': contract.end_date,  # Дата окончания
            'days_until_expiry': (contract.end_date - today).days,  # Сколько дней осталось до окончания
            'is_expired': contract.end_date < today  # Флаг: истёк ли контракт
        })
    return result  # Возвращаем список словарей


def get_expiring_licenses(db: Session, days_threshold: int = 30) -> List[Dict[str, Any]]:  # Получить лицензии, срок которых скоро истекает
    validate_positive_int(days_threshold, "Пороговое значение дней")  # Проверяем порог
    today = date.today()  # Сегодняшняя дата
    threshold_date = today + timedelta(days=days_threshold)  # Дата порога

    expiring_licenses = db.query(License).filter(  # Запрашиваем лицензии
        License.end_date >= today,  # Дата окончания не раньше сегодняшней
        License.end_date <= threshold_date  # И не позже пороговой даты
    ).order_by(License.end_date).all()  # Сортируем по дате окончания

    result = []  # Список результатов
    from models.cinema import Film  # Импортируем модель Film для проверки связей
    for license_obj in expiring_licenses:  # Перебираем найденные лицензии
        film = db.query(Film).filter(Film.license_id == license_obj.id).first()  # Проверяем, есть ли фильм с этой лицензией
        result.append({
            'license_id': license_obj.id,  # ID лицензии
            'film_title': license_obj.film_title,  # Название фильма
            'supplier_id': license_obj.supplier_id,  # ID поставщика
            'contract_id': license_obj.contract_id,  # ID контракта
            'end_date': license_obj.end_date,  # Дата окончания
            'days_until_expiry': (license_obj.end_date - today).days,  # Сколько дней осталось
            'is_expired': license_obj.end_date < today,  # Флаг: истекла ли лицензия
            'has_film': film is not None,  # Есть ли связанный фильм
            'film_id': film.id if film else None  # ID фильма, если он есть
        })
    return result  # Возвращаем список словарей


def get_contract_summary(db: Session, contract_id: int) -> Dict[str, Any]:  # Получить сводную информацию по контракту
    validate_positive_int(contract_id, "ID контракта")  # Проверяем ID
    contract = db.query(Contract).filter(Contract.id == contract_id).first()  # Ищем контракт
    if not contract:  # Если контракт не найден
        raise ValueError(f"Контракт с ID {contract_id} не найден")  # Ошибка

    licenses = db.query(License).filter(License.contract_id == contract_id).all()  # Все лицензии контракта
    today = date.today()  # Сегодняшняя дата
    active_licenses = [l for l in licenses if l.start_date <= today and l.end_date >= today]  # Активные лицензии

    from models.cinema import Film  # Импортируем модель Film
    used_license_ids = [lid[0] for lid in db.query(Film.license_id).filter(Film.license_id.isnot(None)).all()]  # ID используемых лицензий
    used_licenses = [l for l in licenses if l.id in used_license_ids]  # Список используемых лицензий
    unused_licenses = [l for l in licenses if l.id not in used_license_ids]  # Список неиспользуемых лицензий

    return {  # Возвращаем словарь со сводной информацией
        'contract_id': contract.id,
        'title': contract.title,
        'supplier_id': contract.supplier_id,
        'start_date': contract.start_date,
        'end_date': contract.end_date,
        'is_active': contract.start_date <= today and contract.end_date >= today,  # Флаг: активен ли контракт
        'total_licenses': len(licenses),  # Всего лицензий
        'active_licenses': len(active_licenses),  # Активных лицензий
        'used_licenses': len(used_licenses),  # Используемых лицензий
        'unused_licenses': len(unused_licenses),  # Неиспользуемых лицензий
        'days_remaining': (contract.end_date - today).days if contract.end_date >= today else 0,  # Сколько дней осталось
        'licenses': [  # Список лицензий с деталями
            {
                'license_id': l.id,
                'film_title': l.film_title,
                'start_date': l.start_date,
                'end_date': l.end_date,
                'is_active': l.start_date <= today and l.end_date >= today,
                'is_used': l.id in used_license_ids
            }
            for l in licenses
        ]
    }

def get_supplier_contracts_summary(db: Session, supplier_id: int) -> Dict[str, Any]:  # Получить сводку по контрактам поставщика
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем, что ID поставщика — положительное целое число
    contracts = db.query(Contract).filter(Contract.supplier_id == supplier_id).all()  # Запрашиваем все контракты этого поставщика

    today = date.today()  # Получаем сегодняшнюю дату
    active_contracts = [c for c in contracts if c.start_date <= today and c.end_date >= today]  # Список активных контрактов
    expired_contracts = [c for c in contracts if c.end_date < today]  # Список истёкших контрактов
    future_contracts = [c for c in contracts if c.start_date > today]  # Список будущих контрактов

    total_licenses = 0  # Счётчик всех лицензий
    active_licenses = 0  # Счётчик активных лицензий
    for contract in contracts:  # Перебираем все контракты
        licenses = db.query(License).filter(License.contract_id == contract.id).all()  # Получаем лицензии для контракта
        total_licenses += len(licenses)  # Увеличиваем общий счётчик лицензий
        active_licenses += len([l for l in licenses if l.start_date <= today and l.end_date >= today])  # Увеличиваем счётчик активных лицензий

    return {  # Возвращаем словарь со сводной информацией
        'supplier_id': supplier_id,  # ID поставщика
        'total_contracts': len(contracts),  # Всего контрактов
        'active_contracts': len(active_contracts),  # Количество активных контрактов
        'expired_contracts': len(expired_contracts),  # Количество истёкших контрактов
        'future_contracts': len(future_contracts),  # Количество будущих контрактов
        'total_licenses': total_licenses,  # Всего лицензий
        'active_licenses': active_licenses,  # Активных лицензий
        'contracts': [  # Список всех контрактов с деталями
            {
                'contract_id': c.id,  # ID контракта
                'title': c.title,  # Название контракта
                'start_date': c.start_date,  # Дата начала
                'end_date': c.end_date,  # Дата окончания
                'status': 'active' if c.start_date <= today and c.end_date >= today else  # Определяем статус
                          'expired' if c.end_date < today else 'future',  # expired — если истёк, future — если ещё не начался
                'days_remaining': (c.end_date - today).days if c.end_date >= today else 0  # Сколько дней осталось до окончания (или 0, если истёк)
            }
            for c in contracts  # Перебираем все контракты
        ]
    }

def delete_contract(db: Session, contract_id: int) -> bool:
    """Удалить контракт"""
    validate_positive_int(contract_id, "ID контракта")
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        return False

    # Проверяем, есть ли связанные лицензии
    license_count = db.query(License).filter(License.contract_id == contract_id).count()
    if license_count > 0:
        # Можно предложить удалить лицензии или показать ошибку
        # Пока просто запрещаем удаление
        raise ValueError(f"Невозможно удалить контракт: есть {license_count} связанных лицензий")

    # ИСПРАВЛЕНИЕ: убираем with db.begin()
    db.delete(contract)
    db.commit()
    return True

def delete_license(db: Session, license_id: int) -> bool:
    """Удалить лицензию"""
    validate_positive_int(license_id, "ID лицензии")
    license_obj = db.query(License).filter(License.id == license_id).first()
    if not license_obj:
        return False

    # Проверяем, есть ли связанный фильм
    from models.cinema import Film
    film_exists = db.query(Film).filter(Film.license_id == license_id).first()
    if film_exists:
        raise ValueError(f"Невозможно удалить лицензию: есть связанный фильм (ID: {film_exists.id})")

    # ИСПРАВЛЕНИЕ: убираем with db.begin()
    db.delete(license_obj)
    db.commit()
    return True