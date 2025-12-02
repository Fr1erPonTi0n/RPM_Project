from sqlalchemy.orm import Session  # Импортируем Session — объект для работы с базой данных
from sqlalchemy import func, and_, or_  # Импортируем функции: func (агрегация), and_, or_ (логические операторы для фильтров)
from typing import List, Optional, Dict, Any  # Импортируем типы данных для аннотаций
from models.supplier import Supplier, SupplyType, supplier_supply_type  # Импортируем ORM-модели: поставщик, тип поставки и таблицу связей


# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ВАЛИДАЦИИ

def validate_positive_int(value: int, name: str) -> None:  # Проверка положительного целого числа
    if not isinstance(value, int) or value <= 0:  # Если значение не int или меньше/равно 0
        raise ValueError(f"{name} должен быть положительным целым числом, получено: {value}")  # Ошибка


def validate_string(value: str, name: str, min_len: int = 1) -> None:  # Проверка строки
    if not isinstance(value, str) or len(value.strip()) < min_len:  # Если не строка или слишком короткая
        raise ValueError(f"{name} должно быть строкой длиной минимум {min_len} символов")  # Ошибка

def create_supplier(db: Session, name: str, contact_info: str = "",
                    details: str = "", supply_type_ids: Optional[List[int]] = None) -> Supplier:  # Создать нового поставщика
    validate_string(name, "Имя поставщика", min_len=2)  # Проверяем имя (минимум 2 символа)

    existing_supplier = db.query(Supplier).filter(
        func.lower(Supplier.name) == func.lower(name)).first()  # Проверяем, есть ли поставщик с таким именем
    if existing_supplier:  # Если найден дубликат
        raise ValueError(f"Поставщик с именем '{name}' уже существует (ID: {existing_supplier.id})")  # Ошибка

    new_supplier = Supplier(  # Создаём объект поставщика
        name=name.strip(),  # Имя (убираем пробелы)
        contact_info=contact_info.strip() if contact_info else None,  # Контактная информация
        details=details.strip() if details else None  # Дополнительные реквизиты
    )

    with db.begin():  # Транзакция
        db.add(new_supplier)  # Добавляем поставщика в базу

    db.refresh(new_supplier)  # Обновляем объект (чтобы получить ID)

    if supply_type_ids:  # Если указаны типы поставок
        for type_id in supply_type_ids:  # Перебираем список ID
            validate_positive_int(type_id, "ID типа поставки")  # Проверяем ID
            supply_type = db.query(SupplyType).filter(SupplyType.id == type_id).first()  # Ищем тип поставки
            if not supply_type:  # Если тип не найден
                raise ValueError(f"Тип поставки с ID {type_id} не найден")  # Ошибка

        with db.begin():  # Транзакция для добавления связей
            for type_id in supply_type_ids:  # Перебираем ID типов
                db.execute(supplier_supply_type.insert().values(  # Добавляем запись в таблицу связей
                    supplier_id=new_supplier.id,
                    supply_type_id=type_id
                ))

    db.refresh(new_supplier)  # Обновляем объект с новыми связями
    return new_supplier  # Возвращаем созданного поставщика

def get_all_suppliers(db: Session, name_filter: Optional[str] = None,
                      supply_type_id: Optional[int] = None) -> List[Supplier]:  # Получить список всех поставщиков
    query = db.query(Supplier)  # Базовый запрос ко всем поставщикам

    if name_filter:  # Если указан фильтр по имени
        validate_string(name_filter, "Фильтр по имени")  # Проверяем строку
        query = query.filter(Supplier.name.ilike(f"%{name_filter.strip()}%"))  # Фильтруем по частичному совпадению имени

    if supply_type_id is not None:  # Если указан фильтр по типу поставки
        validate_positive_int(supply_type_id, "ID типа поставки")  # Проверяем ID
        query = query.join(supplier_supply_type).filter(  # Присоединяем таблицу связей
            supplier_supply_type.c.supply_type_id == supply_type_id  # Фильтруем по типу поставки
        )

    return query.order_by(Supplier.name).all()  # Сортируем по имени и возвращаем список


def get_supplier_by_id(db: Session, supplier_id: int) -> Optional[Supplier]:  # Получить поставщика по ID
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()  # Ищем поставщика в базе


def update_supplier(db: Session, supplier_id: int, name: Optional[str] = None,
                    contact_info: Optional[str] = None, details: Optional[str] = None) -> Optional[Supplier]:  # Обновить данные поставщика
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()  # Ищем поставщика
    if not supplier:  # Если поставщик не найден
        return None  # Возвращаем None

    if name is not None:  # Если нужно обновить имя
        validate_string(name, "Имя поставщика", min_len=2)  # Проверяем строку
        existing = db.query(Supplier).filter(  # Проверяем, нет ли другого поставщика с таким именем
            func.lower(Supplier.name) == func.lower(name.strip()),
            Supplier.id != supplier_id
        ).first()
        if existing:  # Если нашли дубликат
            raise ValueError(f"Поставщик с именем '{name}' уже существует (ID: {existing.id})")  # Ошибка
        supplier.name = name.strip()  # Обновляем имя

    if contact_info is not None:  # Если нужно обновить контакты
        supplier.contact_info = contact_info.strip() if contact_info else None  # Обновляем

    if details is not None:  # Если нужно обновить реквизиты
        supplier.details = details.strip() if details else None  # Обновляем

    with db.begin():  # Транзакция
        db.add(supplier)  # Сохраняем изменения

    db.refresh(supplier)  # Обновляем объект
    return supplier  # Возвращаем обновлённого поставщика

def add_supply_type_to_supplier(db: Session, supplier_id: int,
                                supply_type_id: int) -> bool:  # Добавить тип поставки поставщику
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID поставщика
    validate_positive_int(supply_type_id, "ID типа поставки")  # Проверяем ID типа поставки

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()  # Ищем поставщика
    if not supplier:  # Если поставщик не найден
        raise ValueError(f"Поставщик с ID {supplier_id} не найден")  # Ошибка

    supply_type = db.query(SupplyType).filter(SupplyType.id == supply_type_id).first()  # Ищем тип поставки
    if not supply_type:  # Если тип поставки не найден
        raise ValueError(f"Тип поставки с ID {supply_type_id} не найден")  # Ошибка

    existing = db.execute(  # Проверяем, есть ли уже такая связь
        supplier_supply_type.select().where(
            and_(
                supplier_supply_type.c.supplier_id == supplier_id,
                supplier_supply_type.c.supply_type_id == supply_type_id
            )
        )
    ).first()

    if existing:  # Если связь уже существует
        return False  # Возвращаем False (ничего не добавили)

    with db.begin():  # Транзакция
        db.execute(  # Добавляем связь в таблицу
            supplier_supply_type.insert().values(
                supplier_id=supplier_id,
                supply_type_id=supply_type_id
            )
        )

    return True  # Возвращаем True (успешно добавили)


def remove_supply_type_from_supplier(db: Session, supplier_id: int,
                                     supply_type_id: int) -> bool:  # Удалить тип поставки у поставщика
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID поставщика
    validate_positive_int(supply_type_id, "ID типа поставки")  # Проверяем ID типа поставки

    existing = db.execute(  # Проверяем, есть ли такая связь
        supplier_supply_type.select().where(
            and_(
                supplier_supply_type.c.supplier_id == supplier_id,
                supplier_supply_type.c.supply_type_id == supply_type_id
            )
        )
    ).first()

    if not existing:  # Если связи нет
        return False  # Возвращаем False (ничего не удалили)

    with db.begin():  # Транзакция
        db.execute(  # Удаляем связь
            supplier_supply_type.delete().where(
                and_(
                    supplier_supply_type.c.supplier_id == supplier_id,
                    supplier_supply_type.c.supply_type_id == supply_type_id
                )
            )
        )

    return True  # Возвращаем True (успешно удалили)


def delete_supplier(db: Session, supplier_id: int) -> bool:  # Удалить поставщика
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID поставщика

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()  # Ищем поставщика
    if not supplier:  # Если поставщик не найден
        return False  # Возвращаем False

    # Проверяем связанные сущности
    from models.license import Contract, License  # Импортируем модели контрактов и лицензий
    from models.procurement import OrderSupliers  # Импортируем модель заказов

    contract_count = db.query(Contract).filter(Contract.supplier_id == supplier_id).count()  # Считаем контракты
    if contract_count > 0:  # Если есть контракты
        raise ValueError(f"Невозможно удалить поставщика: есть {contract_count} связанных контрактов")  # Ошибка

    license_count = db.query(License).filter(License.supplier_id == supplier_id).count()  # Считаем лицензии
    if license_count > 0:  # Если есть лицензии
        raise ValueError(f"Невозможно удалить поставщика: есть {license_count} связанных лицензий")  # Ошибка

    order_count = db.query(OrderSupliers).filter(OrderSupliers.supplier_id == supplier_id).count()  # Считаем заказы
    if order_count > 0:  # Если есть заказы
        raise ValueError(f"Невозможно удалить поставщика: есть {order_count} связанных заказов")  # Ошибка

    with db.begin():  # Транзакция
        db.execute(  # Удаляем все связи с типами поставок
            supplier_supply_type.delete().where(
                supplier_supply_type.c.supplier_id == supplier_id
            )
        )
        db.delete(supplier)  # Удаляем самого поставщика

    return True  # Возвращаем True (успешно удалили)

# РАБОТА С ТИПАМИ ПОСТАВОК

def create_supply_type(db: Session, name: str, description: str = "") -> SupplyType:  # Создать новый тип поставки
    validate_string(name, "Название типа поставки", min_len=2)  # Проверяем, что название — строка длиной ≥ 2 символа

    existing_type = db.query(SupplyType).filter(
        func.lower(SupplyType.name) == func.lower(name)).first()  # Проверяем, есть ли тип с таким названием
    if existing_type:  # Если найден дубликат
        raise ValueError(f"Тип поставки с названием '{name}' уже существует (ID: {existing_type.id})")  # Ошибка

    new_type = SupplyType(  # Создаём объект типа поставки
        name=name.strip(),  # Название (убираем пробелы)
        description=description.strip() if description else None  # Описание (если указано)
    )

    with db.begin():  # Транзакция
        db.add(new_type)  # Добавляем тип в базу

    db.refresh(new_type)  # Обновляем объект (чтобы получить ID)
    return new_type  # Возвращаем созданный тип


def get_all_supply_types(db: Session) -> List[SupplyType]:  # Получить список всех типов поставок
    return db.query(SupplyType).order_by(SupplyType.name).all()  # Сортируем по имени и возвращаем список


def get_supply_type_by_id(db: Session, type_id: int) -> Optional[SupplyType]:  # Получить тип поставки по ID
    validate_positive_int(type_id, "ID типа поставки")  # Проверяем ID
    return db.query(SupplyType).filter(SupplyType.id == type_id).first()  # Ищем тип в базе


def update_supply_type(db: Session, type_id: int, name: Optional[str] = None,
                       description: Optional[str] = None) -> Optional[SupplyType]:  # Обновить тип поставки
    validate_positive_int(type_id, "ID типа поставки")  # Проверяем ID

    supply_type = db.query(SupplyType).filter(SupplyType.id == type_id).first()  # Ищем тип
    if not supply_type:  # Если тип не найден
        return None  # Возвращаем None

    if name is not None:  # Если нужно обновить название
        validate_string(name, "Название типа поставки", min_len=2)  # Проверяем строку
        existing = db.query(SupplyType).filter(  # Проверяем, нет ли другого типа с таким названием
            func.lower(SupplyType.name) == func.lower(name.strip()),
            SupplyType.id != type_id
        ).first()
        if existing:  # Если нашли дубликат
            raise ValueError(f"Тип поставки с названием '{name}' уже существует (ID: {existing.id})")  # Ошибка
        supply_type.name = name.strip()  # Обновляем название

    if description is not None:  # Если нужно обновить описание
        supply_type.description = description.strip() if description else None  # Обновляем описание

    with db.begin():  # Транзакция
        db.add(supply_type)  # Сохраняем изменения

    db.refresh(supply_type)  # Обновляем объект
    return supply_type  # Возвращаем обновлённый тип


def delete_supply_type(db: Session, type_id: int) -> bool:  # Удалить тип поставки
    validate_positive_int(type_id, "ID типа поставки")  # Проверяем ID

    supply_type = db.query(SupplyType).filter(SupplyType.id == type_id).first()  # Ищем тип
    if not supply_type:  # Если тип не найден
        return False  # Возвращаем False

    supplier_count = db.execute(  # Проверяем, есть ли поставщики с этим типом
        supplier_supply_type.select().where(
            supplier_supply_type.c.supply_type_id == type_id
        )
    ).fetchall()

    if len(supplier_count) > 0:  # Если есть связанные поставщики
        raise ValueError(f"Невозможно удалить тип поставки: есть {len(supplier_count)} связанных поставщиков")  # Ошибка

    with db.begin():  # Транзакция
        db.delete(supply_type)  # Удаляем тип поставки

    return True  # Возвращаем True (успешно удалили)

# АНАЛИТИКА ПОСТАВЩИКОВ

def get_supplier_stats(db: Session, supplier_id: int) -> Dict[str, Any]:  # Получить статистику по поставщику
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()  # Ищем поставщика
    if not supplier:  # Если поставщик не найден
        raise ValueError(f"Поставщик с ID {supplier_id} не найден")  # Ошибка

    # Импортируем связанные модели для анализа
    from models.license import Contract, License  # Контракты и лицензии
    from models.procurement import OrderSupliers  # Заказы поставщикам
    from models.analytics import SupplierKPI  # KPI поставщика

    contracts = db.query(Contract).filter(Contract.supplier_id == supplier_id).all()  # Все контракты
    active_contracts = [c for c in contracts if c.end_date >= date.today()]  # Активные контракты

    licenses = db.query(License).filter(License.supplier_id == supplier_id).all()  # Все лицензии
    active_licenses = [l for l in licenses if l.end_date >= date.today()]  # Активные лицензии

    orders = db.query(OrderSupliers).filter(OrderSupliers.supplier_id == supplier_id).all()  # Все заказы
    delivered_orders = [o for o in orders if o.status == "доставлен"]  # Доставленные заказы

    kpi = db.query(SupplierKPI).filter(SupplierKPI.supplier_id == supplier_id).order_by(
        SupplierKPI.calculation_date.desc()
    ).first()  # Последняя запись KPI

    return {  # Возвращаем словарь со статистикой
        'supplier_id': supplier_id,
        'supplier_name': supplier.name,
        'total_contracts': len(contracts),
        'active_contracts': len(active_contracts),
        'total_licenses': len(licenses),
        'active_licenses': len(active_licenses),
        'total_orders': len(orders),
        'delivered_orders': len(delivered_orders),
        'recent_kpi': {  # Последняя оценка KPI
            'overall_rating': round(kpi.overall_rating, 2) if kpi else None,
            'on_time_delivery': round(kpi.on_time_delivery, 2) if kpi else None,
            'calculation_date': kpi.calculation_date if kpi else None
        } if kpi else None,
        'supply_types': [st.name for st in supplier.supply_types]  # Типы поставок
    }


def get_suppliers_by_supply_type(db: Session, supply_type_id: int) -> List[Dict[str, Any]]:  # Получить поставщиков по типу поставки
    validate_positive_int(supply_type_id, "ID типа поставки")  # Проверяем ID

    supply_type = db.query(SupplyType).filter(SupplyType.id == supply_type_id).first()  # Ищем тип поставки
    if not supply_type:  # Если тип не найден
        raise ValueError(f"Тип поставки с ID {supply_type_id} не найден")  # Ошибка

    suppliers = db.query(Supplier).join(supplier_supply_type).filter(  # Получаем поставщиков с этим типом
        supplier_supply_type.c.supply_type_id == supply_type_id
    ).order_by(Supplier.name).all()

    result = []  # Список для результатов
    for supplier in suppliers:  # Перебираем поставщиков
        from models.license import Contract  # Импортируем контракты
        active_contracts = db.query(Contract).filter(  # Считаем активные контракты
            Contract.supplier_id == supplier.id,
            Contract.end_date >= date.today()
        ).count()

        result.append({  # Добавляем информацию о поставщике
            'supplier_id': supplier.id,
            'supplier_name': supplier.name,
            'contact_info': supplier.contact_info,
            'active_contracts': active_contracts,
            'total_supply_types': len(supplier.supply_types)
        })

    return result  # Возвращаем список словарей


def search_suppliers(db: Session, search_term: str,
                     limit: int = 20) -> List[Dict[str, Any]]:  # Поиск поставщиков по строке
    validate_string(search_term, "Поисковый запрос", min_len=2)  # Проверяем поисковый запрос
    validate_positive_int(limit, "Лимит результатов")  # Проверяем лимит

    suppliers = db.query(Supplier).filter(  # Ищем поставщиков по имени, контактам или реквизитам
        or_(
            Supplier.name.ilike(f"%{search_term.strip()}%"),
            Supplier.contact_info.ilike(f"%{search_term.strip()}%"),
            Supplier.details.ilike(f"%{search_term.strip()}%")
        )
    ).order_by(Supplier.name).limit(limit).all()

    result = []  # Список для результатов
    for supplier in suppliers:  # Перебираем найденных поставщиков
        result.append({
            'supplier_id': supplier.id,
            'supplier_name': supplier.name,
            'contact_info': supplier.contact_info,
            'supply_types': [st.name for st in supplier.supply_types]  # Типы поставок
        })

    return result  # Возвращаем список найденных поставщиков
