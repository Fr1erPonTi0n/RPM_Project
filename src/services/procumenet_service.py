from sqlalchemy.orm import Session  # Импортируем класс Session из SQLAlchemy — нужен для работы с базой данных
from sqlalchemy import func  # Импортируем функции для агрегации (например, count, sum)
from datetime import datetime, date  # Импортируем классы для работы с датами
from typing import List, Optional, Dict, Any  # Импортируем типы для аннотаций
from models.procurement import OrderSupliers, OrderClients, OrderItem  # Импортируем ORM-модели для заказов


# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ВАЛИДАЦИИ

def validate_positive_int(value: int, name: str) -> None:  # Проверка положительного целого числа
    if not isinstance(value, int) or value <= 0:  # Если значение не int или <= 0
        raise ValueError(f"{name} должен быть положительным целым числом, получено: {value}")  # Ошибка


def validate_string(value: str, name: str, min_len: int = 1) -> None:  # Проверка строки
    if not isinstance(value, str) or len(value.strip()) < min_len:  # Если не строка или слишком короткая
        raise ValueError(f"{name} должно быть строкой длиной минимум {min_len} символов")  # Ошибка


def validate_price(value: float, name: str = "Цена") -> None:  # Проверка цены
    if not isinstance(value, (int, float)) or value <= 0:  # Если не число или <= 0
        raise ValueError(f"{name} должна быть положительным числом, получено: {value}")  # Ошибка


def validate_quantity(value: int, name: str = "Количество") -> None:  # Проверка количества
    if not isinstance(value, int) or value <= 0:  # Если не int или <= 0
        raise ValueError(f"{name} должно быть положительным целым числом, получено: {value}")  # Ошибка


def parse_date(date_str: str) -> date:  # Парсинг даты из строки
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()  # Преобразуем строку в объект date (формат YYYY-MM-DD)
    except ValueError:  # Если формат неверный
        raise ValueError(f"Некорректный формат даты: {date_str}. Используйте YYYY-MM-DD")  # Ошибка


def validate_status(value: str, valid_statuses: List[str], name: str = "Статус") -> None:  # Проверка статуса
    if value not in valid_statuses:  # Если статус не входит в список допустимых
        raise ValueError(f"{name} должен быть одним из: {', '.join(valid_statuses)}, получено: {value}")  # Ошибка


# РАБОТА С ЗАКАЗАМИ ПОСТАВЩИКАМ

def create_supplier_order(db: Session, supplier_id: int, contract_id: int,
                          delivery_date_str: Optional[str] = None) -> OrderSupliers:  # Создание заказа поставщику
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID поставщика
    validate_positive_int(contract_id, "ID контракта")  # Проверяем ID контракта

    delivery_date = None  # Инициализируем дату доставки как None
    if delivery_date_str:  # Если дата доставки указана
        delivery_date = parse_date(delivery_date_str)  # Преобразуем строку в объект date
        if delivery_date < date.today():  # Если дата доставки в прошлом
            raise ValueError("Дата доставки не может быть в прошлом")  # Ошибка

    new_order = OrderSupliers(  # Создаём объект заказа
        supplier_id=supplier_id,  # ID поставщика
        contract_id=contract_id,  # ID контракта
        status="создан",  # Статус заказа по умолчанию
        created_date=datetime.now(),  # Дата создания — текущая
        delivery_date=delivery_date,  # Дата доставки (может быть None)
        total_amount=0.0  # Начальная сумма заказа
    )

    with db.begin():  # Открываем транзакцию
        db.add(new_order)  # Добавляем заказ в базу
    db.refresh(new_order)  # Обновляем объект из базы
    return new_order  # Возвращаем созданный заказ

def get_all_supplier_orders(db: Session, supplier_id: Optional[int] = None,
                            status: Optional[str] = None) -> List[OrderSupliers]:  # Получить список заказов поставщикам
    query = db.query(OrderSupliers)  # Базовый запрос ко всем заказам

    if supplier_id is not None:  # Если указан ID поставщика
        validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID
        query = query.filter(OrderSupliers.supplier_id == supplier_id)  # Фильтруем по поставщику

    if status is not None:  # Если указан статус
        valid_statuses = ["создан", "в процессе", "доставлен", "отменен"]  # Допустимые статусы
        validate_status(status, valid_statuses, "Статус заказа")  # Проверяем статус
        query = query.filter(OrderSupliers.status == status)  # Фильтруем по статусу

    return query.order_by(OrderSupliers.created_date.desc()).all()  # Сортируем по дате создания и возвращаем список


def get_supplier_order_by_id(db: Session, order_id: int) -> Optional[OrderSupliers]:  # Получить заказ по ID
    validate_positive_int(order_id, "ID заказа")  # Проверяем ID заказа
    return db.query(OrderSupliers).filter(OrderSupliers.id == order_id).first()  # Ищем заказ в базе


def update_supplier_order_status(db: Session, order_id: int,
                                 new_status: str) -> Optional[OrderSupliers]:  # Обновить статус заказа
    validate_positive_int(order_id, "ID заказа")  # Проверяем ID заказа
    valid_statuses = ["создан", "в процессе", "доставлен", "отменен"]  # Допустимые статусы
    validate_status(new_status, valid_statuses, "Статус заказа")  # Проверяем новый статус

    order = db.query(OrderSupliers).filter(OrderSupliers.id == order_id).first()  # Ищем заказ
    if not order:  # Если заказ не найден
        return None  # Возвращаем None

    order.status = new_status  # Обновляем статус
    if new_status == "доставлен":  # Если заказ доставлен
        order.delivery_date = date.today()  # Устанавливаем сегодняшнюю дату как дату доставки

    with db.begin():  # Транзакция
        db.add(order)  # Сохраняем изменения
    db.refresh(order)  # Обновляем объект
    return order  # Возвращаем обновлённый заказ


def add_item_to_supplier_order(db: Session, order_id: int,
                               product_name: str, quantity: int, price: float) -> OrderItem:  # Добавить товар в заказ
    validate_positive_int(order_id, "ID заказа")  # Проверяем ID заказа
    validate_string(product_name, "Название товара", 2)  # Проверяем название товара
    validate_quantity(quantity, "Количество товара")  # Проверяем количество
    validate_price(price, "Цена товара")  # Проверяем цену

    order = db.query(OrderSupliers).filter(OrderSupliers.id == order_id).first()  # Ищем заказ
    if not order:  # Если заказ не найден
        raise ValueError(f"Заказ с ID {order_id} не найден")  # Ошибка

    if order.status == "отменен":  # Если заказ отменён
        raise ValueError("Нельзя добавить товар в отмененный заказ")  # Ошибка

    total_price = quantity * price  # Считаем общую стоимость товара

    new_item = OrderItem(  # Создаём объект товара
        order_id=order_id,  # ID заказа
        product_name=product_name.strip(),  # Название товара (убираем пробелы)
        quantity=quantity,  # Количество
        price=round(price, 2),  # Цена за единицу
        total_price=round(total_price, 2)  # Общая стоимость
    )

    with db.begin():  # Транзакция
        db.add(new_item)  # Добавляем товар
        order.total_amount = round(order.total_amount + total_price, 2)  # Обновляем сумму заказа
        db.add(order)  # Сохраняем изменения в заказе

    db.refresh(new_item)  # Обновляем объект товара
    return new_item  # Возвращаем добавленный товар


def get_order_items(db: Session, order_id: int) -> List[OrderItem]:  # Получить список товаров заказа
    validate_positive_int(order_id, "ID заказа")  # Проверяем ID заказа
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).order_by(OrderItem.id).all()  # Возвращаем товары


def delete_supplier_order(db: Session, order_id: int) -> bool:  # Удалить заказ поставщика
    validate_positive_int(order_id, "ID заказа")  # Проверяем ID заказа
    order = db.query(OrderSupliers).filter(OrderSupliers.id == order_id).first()  # Ищем заказ
    if not order:  # Если заказ не найден
        return False  # Возвращаем False

    if order.status == "доставлен":  # Если заказ уже доставлен
        raise ValueError("Нельзя удалить доставленный заказ")  # Ошибка

    with db.begin():  # Транзакция
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()  # Удаляем все товары заказа
        db.delete(order)  # Удаляем сам заказ

    return True

# РАБОТА С ЗАКАЗАМИ КЛИЕНТОВ

def create_client_order(db: Session, client_name: str, phone: str,
                        total_amount: float = 0.0) -> OrderClients:  # Создать заказ клиента
    validate_string(client_name, "Имя клиента", 2)  # Проверяем, что имя клиента — строка длиной ≥ 2 символа
    validate_string(phone, "Телефон клиента", 5)  # Проверяем, что телефон — строка длиной ≥ 5 символов

    if total_amount < 0:  # Если сумма заказа отрицательная
        raise ValueError("Сумма заказа не может быть отрицательной")  # Ошибка

    new_order = OrderClients(  # Создаём объект заказа клиента
        client_name=client_name.strip(),  # Имя клиента (убираем пробелы)
        phone=phone.strip(),  # Телефон (убираем пробелы)
        order_date=datetime.now(),  # Дата заказа — текущая
        total_amount=round(total_amount, 2),  # Общая сумма заказа (округляем до 2 знаков)
        status="оформлен"  # Статус заказа по умолчанию
    )

    with db.begin():  # Транзакция
        db.add(new_order)  # Добавляем заказ в базу
    db.refresh(new_order)  # Обновляем объект
    return new_order  # Возвращаем созданный заказ


def get_all_client_orders(db: Session, status: Optional[str] = None,
                          start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[OrderClients]:  # Получить список заказов клиентов
    query = db.query(OrderClients)  # Базовый запрос ко всем заказам клиентов

    if status is not None:  # Если указан статус
        validate_string(status, "Статус заказа")  # Проверяем статус
        query = query.filter(OrderClients.status == status)  # Фильтруем по статусу

    if start_date:  # Если указана начальная дата
        start = parse_date(start_date)  # Парсим дату
        query = query.filter(OrderClients.order_date >= datetime.combine(start, datetime.min.time()))  # Фильтруем по дате начала

    if end_date:  # Если указана конечная дата
        end = parse_date(end_date)  # Парсим дату
        query = query.filter(OrderClients.order_date <= datetime.combine(end, datetime.max.time()))  # Фильтруем по дате окончания

    return query.order_by(OrderClients.order_date.desc()).all()  # Сортируем по дате заказа и возвращаем список


def get_client_order_by_id(db: Session, order_id: int) -> Optional[OrderClients]:  # Получить заказ клиента по ID
    validate_positive_int(order_id, "ID заказа клиента")  # Проверяем ID заказа
    return db.query(OrderClients).filter(OrderClients.id == order_id).first()  # Ищем заказ в базе


def update_client_order_status(db: Session, order_id: int,
                               new_status: str) -> Optional[OrderClients]:  # Обновить статус заказа клиента
    validate_positive_int(order_id, "ID заказа клиента")  # Проверяем ID заказа

    order = db.query(OrderClients).filter(OrderClients.id == order_id).first()  # Ищем заказ
    if not order:  # Если заказ не найден
        return None  # Возвращаем None

    validate_string(new_status, "Статус заказа")  # Проверяем новый статус
    order.status = new_status  # Обновляем статус

    with db.begin():  # Транзакция
        db.add(order)  # Сохраняем изменения
    db.refresh(order)  # Обновляем объект
    return order  # Возвращаем обновлённый заказ


def update_client_order_amount(db: Session, order_id: int,
                               new_amount: float) -> Optional[OrderClients]:  # Обновить сумму заказа клиента
    validate_positive_int(order_id, "ID заказа клиента")  # Проверяем ID заказа
    if new_amount < 0:  # Если сумма отрицательная
        raise ValueError("Сумма заказа не может быть отрицательной")  # Ошибка

    order = db.query(OrderClients).filter(OrderClients.id == order_id).first()  # Ищем заказ
    if not order:  # Если заказ не найден
        return None  # Возвращаем None

    order.total_amount = round(new_amount, 2)  # Обновляем сумму заказа (округляем до 2 знаков)

    with db.begin():  # Транзакция
        db.add(order)  # Сохраняем изменения
    db.refresh(order)  # Обновляем объект
    return order  # Возвращаем обновлённый заказ


def delete_client_order(db: Session, order_id: int) -> bool:  # Удалить заказ клиента
    validate_positive_int(order_id, "ID заказа клиента")  # Проверяем ID заказа
    order = db.query(OrderClients).filter(OrderClients.id == order_id).first()  # Ищем заказ
    if not order:  # Если заказ не найден
        return False  # Возвращаем False

    with db.begin():  # Транзакция
        db.delete(order)  # Удаляем заказ

    return True

# АНАЛИТИКА ЗАКУПОК

def get_supplier_order_stats(db: Session, supplier_id: int,
                             start_date_str: Optional[str] = None,
                             end_date_str: Optional[str] = None) -> Dict[str, Any]:  # Получить статистику заказов поставщика
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID поставщика

    query = db.query(OrderSupliers).filter(OrderSupliers.supplier_id == supplier_id)  # Базовый запрос по заказам поставщика

    if start_date_str:  # Если указана начальная дата
        start_date = parse_date(start_date_str)  # Преобразуем строку в дату
        query = query.filter(OrderSupliers.created_date >= datetime.combine(start_date, datetime.min.time()))  # Фильтруем по дате начала

    if end_date_str:  # Если указана конечная дата
        end_date = parse_date(end_date_str)  # Преобразуем строку в дату
        query = query.filter(OrderSupliers.created_date <= datetime.combine(end_date, datetime.max.time()))  # Фильтруем по дате окончания

    all_orders = query.all()  # Получаем все заказы
    total_orders = len(all_orders)  # Считаем количество заказов

    if total_orders == 0:  # Если заказов нет
        return {  # Возвращаем пустую статистику
            'supplier_id': supplier_id,
            'total_orders': 0,
            'total_amount': 0,
            'status_counts': {},
            'average_order_amount': 0
        }

    status_counts = {}  # Словарь для подсчёта заказов по статусам
    total_amount = 0  # Общая сумма заказов

    for order in all_orders:  # Перебираем все заказы
        status_counts[order.status] = status_counts.get(order.status, 0) + 1  # Увеличиваем счётчик для статуса
        total_amount += order.total_amount  # Суммируем общую сумму

    average_amount = round(total_amount / total_orders, 2)  # Средняя сумма заказа

    return {  # Возвращаем статистику
        'supplier_id': supplier_id,
        'total_orders': total_orders,
        'total_amount': round(total_amount, 2),
        'status_counts': status_counts,
        'average_order_amount': average_amount
    }


def get_daily_client_revenue(db: Session, date_str: str) -> Dict[str, Any]:  # Получить выручку за день
    target_date = parse_date(date_str)  # Преобразуем строку в дату
    if target_date > date.today():  # Если дата в будущем
        raise ValueError("Нельзя получить статистику за будущую дату")  # Ошибка

    start_datetime = datetime.combine(target_date, datetime.min.time())  # Начало дня
    end_datetime = datetime.combine(target_date, datetime.max.time())  # Конец дня

    orders = db.query(OrderClients).filter(  # Запрос заказов клиентов за день
        OrderClients.order_date >= start_datetime,
        OrderClients.order_date <= end_datetime
    ).all()

    total_revenue = sum(order.total_amount for order in orders)  # Суммируем выручку
    total_orders = len(orders)  # Считаем количество заказов

    return {  # Возвращаем статистику
        'date': target_date.isoformat(),
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'average_order_amount': round(total_revenue / total_orders, 2) if total_orders > 0 else 0
    }


def get_top_suppliers(db: Session, limit: int = 5,
                      days: int = 30) -> List[Dict[str, Any]]:  # Получить топ поставщиков по объёму заказов
    validate_positive_int(limit, "Лимит")  # Проверяем лимит
    validate_positive_int(days, "Количество дней")  # Проверяем количество дней

    start_date = datetime.now() - timedelta(days=days)  # Дата начала периода (текущая дата минус days)

    results = db.query(  # Запрос для агрегации данных по поставщикам
        OrderSupliers.supplier_id,
        func.count(OrderSupliers.id).label('total_orders'),  # Количество заказов
        func.sum(OrderSupliers.total_amount).label('total_amount')  # Общая сумма заказов
    ).filter(
        OrderSupliers.created_date >= start_date,  # Фильтруем по дате
        OrderSupliers.status != "отменен"  # Исключаем отменённые заказы
    ).group_by(
        OrderSupliers.supplier_id  # Группируем по поставщику
    ).order_by(
        func.sum(OrderSupliers.total_amount).desc()  # Сортируем по сумме заказов (по убыванию)
    ).limit(limit).all()  # Ограничиваем количество результатов

    top_suppliers = []  # Список для результатов
    for idx, (supplier_id, total_orders, total_amount) in enumerate(results):  # Перебираем результаты
        top_suppliers.append({  # Добавляем данные поставщика
            'rank': idx + 1,  # Ранг (место в топе)
            'supplier_id': supplier_id,  # ID поставщика
            'total_orders': total_orders or 0,  # Количество заказов
            'total_amount': round(float(total_amount or 0), 2),  # Общая сумма
            'average_order_amount': round(float(total_amount or 0) / (total_orders or 1), 2)  # Средняя сумма заказа
        })

    return top_suppliers  # Возвращаем список топ поставщиков

