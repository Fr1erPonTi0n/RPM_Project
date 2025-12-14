from sqlalchemy.orm import Session  # Работа с сессией SQLAlchemy
from sqlalchemy import func, and_  # Агрегатные функции и логические операторы
from datetime import datetime, timedelta  # Работа с датами
from typing import List, Optional, Dict, Any  # Типизация
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cinema import Film, Screening, Ticket  # ORM-модели
from utils.validators import validate_positive_int, validate_string, validate_price
from utils.helper import parse_date

# РАБОТА С ФИЛЬМАМИ
def create_film(db: Session, license_id: int, title: str, duration: int, description: str = "") -> Film:  # Создать фильм
    validate_positive_int(license_id, "ID лицензии")  # Проверка ID лицензии
    validate_string(title, "Название фильма")  # Проверка названия
    validate_positive_int(duration, "Длительность фильма")  # Проверка длительности
    if duration > 300:  # Ограничение по длительности
        raise ValueError(f"Длительность фильма не может превышать 300 минут, получено: {duration}")  # Ошибка

    existing_film = db.query(Film).filter(func.lower(Film.title) == func.lower(title)).first()  # Проверка дубликата
    if existing_film:  # Если фильм уже есть
        raise ValueError(f"Фильм '{title}' уже существует (ID: {existing_film.id})")  # Ошибка

    new_film = Film(license_id=license_id, title=title.strip(), duration=duration,
                    description=description.strip() if description else "")  # Создаём объект фильма

    db.add(new_film)
    db.commit()  # Добавляем фильм
    db.refresh(new_film)  # Обновляем объект
    return new_film  # Возвращаем результат


def get_all_films(db: Session, active_only: bool = False) -> List[Film]:  # Получить список фильмов
    query = db.query(Film)  # Базовый запрос
    if active_only:  # Если нужны только активные
        current_time = datetime.now()  # Текущее время
        query = query.join(Screening).filter(Screening.datetime > current_time)  # Фильтр по будущим показам
    return query.order_by(Film.title).all()  # Сортировка и возврат


def get_film_by_id(db: Session, film_id: int) -> Optional[Film]:  # Получить фильм по ID
    validate_positive_int(film_id, "ID фильма")  # Проверка ID
    return db.query(Film).filter(Film.id == film_id).first()  # Запрос по ID


def update_film(db: Session, film_id: int, title: Optional[str] = None,
                duration: Optional[int] = None, description: Optional[str] = None) -> Optional[Film]:  # Обновить фильм
    validate_positive_int(film_id, "ID фильма")  # Проверка ID
    film = db.query(Film).filter(Film.id == film_id).first()  # Поиск фильма
    if not film:  # Если не найден
        return None  # Возвращаем None

    if title is not None:  # Если нужно обновить название
        validate_string(title, "Название фильма")  # Проверка названия
        film.title = title.strip()  # Обновляем

    if duration is not None:  # Если нужно обновить длительность
        validate_positive_int(duration, "Длительность фильма")  # Проверка длительности
        if duration > 300:  # Ограничение
            raise ValueError(f"Длительность фильма не может превышать 300 минут, получено: {duration}")  # Ошибка
        film.duration = duration  # Обновляем

    if description is not None:  # Если нужно обновить описание
        film.description = description.strip() if description else ""  # Обновляем

    db.add(film)
    db.commit()
    db.refresh(film)  # Обновляем объект
    return film  # Возвращаем результат


def delete_film(db: Session, film_id: int) -> bool:  # Удалить фильм
    validate_positive_int(film_id, "ID фильма")  # Проверка ID
    film = db.query(Film).filter(Film.id == film_id).first()  # Поиск фильма
    if not film:  # Если не найден
        return False  # Возвращаем False

    future_screenings = db.query(Screening).filter(Screening.film_id == film_id,
                                                   Screening.datetime > datetime.now()).count()  # Проверяем будущие показы
    if future_screenings > 0:  # Если есть будущие показы
        raise ValueError(f"Невозможно удалить фильм: есть {future_screenings} запланированных показов")  # Ошибка

    db.delete(film)
    db.commit()
    return True

# РАБОТА С ПОКАЗАМИ

def create_screening(db: Session, film_id: int, datetime_str: str, hall: str, ticket_price: float) -> Screening:  # Создать показ
    validate_positive_int(film_id, "ID фильма")  # Проверка ID фильма
    screening_datetime = parse_date(datetime_str)  # Парсим дату
    if screening_datetime < datetime.now():  # Проверка на прошлое
        raise ValueError("Дата и время показа не могут быть в прошлом")  # Ошибка
    validate_string(hall, "Название зала")  # Проверка названия зала
    validate_price(ticket_price, "Цена билета")  # Проверка цены

    film = db.query(Film).filter(Film.id == film_id).first()  # Проверяем фильм
    if not film:  # Если фильм не найден
        raise ValueError(f"Фильм с ID {film_id} не найден")  # Ошибка

    screening_end = screening_datetime + timedelta(minutes=film.duration)  # Конец показа
    conflicting = db.query(Screening).filter(  # Проверка конфликта времени
        Screening.hall == hall,
        and_(Screening.datetime < screening_end,
             func.datetime(Screening.datetime, f'+{film.duration} minutes') > screening_datetime)
    ).first()
    if conflicting:  # Если найден конфликт
        raise ValueError(f"Конфликт времени в зале '{hall}'")  # Ошибка

    new_screening = Screening(film_id=film_id, datetime=screening_datetime,
                              hall=hall.strip(), ticket_price=round(float(ticket_price), 2))  # Создаём показ

    db.add(new_screening)
    db.commit()  # Добавляем показ
    db.refresh(new_screening)  # Обновляем объект
    return new_screening  # Возвращаем результат


def get_all_screenings(db: Session, film_id: Optional[int] = None,
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Screening]:  # Получить показы
    query = db.query(Screening)  # Базовый запрос
    if film_id is not None:  # Фильтр по фильму
        validate_positive_int(film_id, "ID фильма")
        query = query.filter(Screening.film_id == film_id)
    if start_date:  # Фильтр по начальной дате
        query = query.filter(Screening.datetime >= parse_date(start_date))
    if end_date:  # Фильтр по конечной дате
        query = query.filter(Screening.datetime <= parse_date(end_date))
    return query.order_by(Screening.datetime).all()  # Сортировка и возврат


def get_available_screenings(db: Session) -> List[Dict[str, Any]]:  # Получить доступные для покупки показы
    current_time = datetime.now()  # Текущее время
    results = db.query(Screening, Film.title, Film.duration).join(Film, Screening.film_id == Film.id).filter(
        Screening.datetime > current_time).order_by(Screening.datetime).all()  # Запрос будущих показов

    screenings_list = []  # Список результатов
    for screening, film_title, film_duration in results:  # Формируем словари
        screenings_list.append({
            'screening_id': screening.id,
            'film_title': film_title,
            'datetime': screening.datetime,
            'hall': screening.hall,
            'ticket_price': screening.ticket_price,
            'duration_minutes': film_duration,
            'end_time': screening.datetime + timedelta(minutes=film_duration)
        })
    return screenings_list  # Возвращаем список


def update_screening(db: Session, screening_id: int, datetime_str: Optional[str] = None,
                     hall: Optional[str] = None, ticket_price: Optional[float] = None) -> Optional[Screening]:  # Обновить показ
    validate_positive_int(screening_id, "ID показа")  # Проверка ID
    screening = db.query(Screening).filter(Screening.id == screening_id).first()  # Поиск показа
    if not screening:  # Если не найден
        return None
    if screening.datetime < datetime.now():  # Если показ уже прошёл
        raise ValueError("Невозможно изменить информацию о прошедшем показе")  # Ошибка

    if datetime_str is not None:  # Обновление даты
        new_datetime = parse_date(datetime_str)
        if new_datetime < datetime.now():
            raise ValueError("Новая дата и время показа не могут быть в прошлом")
        screening.datetime = new_datetime

    if hall is not None:  # Обновление зала
        validate_string(hall, "Название зала")
        screening.hall = hall.strip()

    if ticket_price is not None:  # Обновление цены
        validate_price(ticket_price, "Цена билета")
        screening.ticket_price = round(float(ticket_price), 2)

    db.add(screening)
    db.commit()
    db.refresh(screening)  # Обновляем объект
    return screening  # Возвращаем результат


def delete_screening(db: Session, screening_id: int) -> bool:  # Удалить показ
    validate_positive_int(screening_id, "ID показа")  # Проверка ID
    screening = db.query(Screening).filter(Screening.id == screening_id).first()  # Поиск показа
    if not screening:  # Если не найден
        return False
    if screening.datetime < datetime.now():  # Если показ уже прошёл
        raise ValueError("Невозможно удалить прошедший показ")  # Ошибка

    sold_tickets = db.query(Ticket).filter(Ticket.screening_id == screening_id, Ticket.sold == True).count()  # Проверка проданных билетов
    if sold_tickets > 0:  # Если есть проданные билеты
        raise ValueError(f"Невозможно удалить показ: продано {sold_tickets} билетов")  # Ошибка

    db.delete(screening)
    db.commit()
    return True

# РАБОТА С БИЛЕТАМИ

def create_ticket(db: Session, screening_id: int, seat_number: str, price: float) -> Ticket:  # Создать билет
    validate_positive_int(screening_id, "ID показа")  # Проверка ID показа
    validate_string(seat_number, "Номер места")  # Проверка номера места
    validate_price(price, "Цена билета")  # Проверка цены

    screening = db.query(Screening).filter(Screening.id == screening_id).first()  # Проверяем показ
    if not screening:
        raise ValueError(f"Показ с ID {screening_id} не найден")  # Ошибка
    if screening.datetime < datetime.now():  # Проверка на прошедший показ
        raise ValueError("Невозможно создать билет на прошедший показ")  # Ошибка

    existing_ticket = db.query(Ticket).filter(Ticket.screening_id == screening_id,
                                              Ticket.seat_number == seat_number.strip()).first()  # Проверка дубликата
    if existing_ticket:
        if existing_ticket.sold:
            raise ValueError(f"Место {seat_number} уже продано")  # Ошибка
        else:
            raise ValueError(f"Место {seat_number} уже существует (билет ID: {existing_ticket.id})")  # Ошибка

    new_ticket = Ticket(screening_id=screening_id, seat_number=seat_number.strip(),
                        price=round(float(price), 2), sold=False, sold_date=None)  # Создаём билет

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket


def get_tickets_by_screening(db: Session, screening_id: int, sold_only: Optional[bool] = None) -> List[Ticket]:  # Получить билеты по показу
    validate_positive_int(screening_id, "ID показа")  # Проверка ID
    query = db.query(Ticket).filter(Ticket.screening_id == screening_id)  # Базовый запрос
    if sold_only is not None:  # Фильтр по статусу продажи
        query = query.filter(Ticket.sold == sold_only)
    return query.order_by(Ticket.seat_number).all()  # Сортировка и возврат


def get_available_seats(db: Session, screening_id: int) -> List[str]:  # Получить свободные места
    validate_positive_int(screening_id, "ID показа")  # Проверка ID
    all_tickets = db.query(Ticket).filter(Ticket.screening_id == screening_id).all()  # Все билеты
    return [ticket.seat_number for ticket in all_tickets if not ticket.sold]  # Только свободные


def sell_ticket(db: Session, ticket_id: int, order_id: Optional[int] = None) -> Optional[Ticket]:  # Продать билет
    validate_positive_int(ticket_id, "ID билета")  # Проверка ID билета
    if order_id is not None:
        validate_positive_int(order_id, "ID заказа")  # Проверка ID заказа

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()  # Поиск билета
    if not ticket:
        return None
    if ticket.sold:  # Если уже продан
        raise ValueError(f"Билет ID {ticket_id} уже продан")  # Ошибка

    screening = db.query(Screening).filter(Screening.id == ticket.screening_id).first()  # Проверка показа
    if screening and screening.datetime < datetime.now():  # Если показ прошёл
        raise ValueError("Невозможно продать билет на прошедший показ")  # Ошибка

    ticket.sold = True  # Отмечаем как проданный
    ticket.sold_date = datetime.now()  # Дата продажи
    if order_id:
        ticket.order_id = order_id  # Привязываем заказ

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def cancel_ticket_sale(db: Session, ticket_id: int) -> Optional[Ticket]:  # Отменить продажу билета
    validate_positive_int(ticket_id, "ID билета")  # Проверка ID
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()  # Поиск билета
    if not ticket:
        return None
    if not ticket.sold:  # Если билет не продан
        raise ValueError(f"Билет ID {ticket_id} не продан, отмена невозможна")  # Ошибка

    screening = db.query(Screening).filter(Screening.id == ticket.screening_id).first()  # Проверка показа
    if screening and screening.datetime < datetime.now():  # Если показ прошёл
        raise ValueError("Невозможно отменить продажу билета на прошедший показ")  # Ошибка

    ticket.sold = False  # Снимаем продажу
    ticket.sold_date = None
    ticket.order_id = None

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: int) -> bool:  # Удалить билет
    validate_positive_int(ticket_id, "ID билета")  # Проверка ID
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()  # Поиск билета
    if not ticket:
        return False
    if ticket.sold:  # Если билет продан
        raise ValueError(f"Невозможно удалить проданный билет (ID: {ticket_id})")  # Ошибка

    db.delete(ticket)
    db.commit()
    return True

# АНАЛИТИКА КИНОТЕАТРА

def get_daily_revenue(db: Session, date_str: str) -> Dict[str, Any]:  # Получить выручку за день
    target_date = parse_date(date_str)  # Парсим дату
    start_datetime = datetime.combine(target_date, datetime.min.time())  # Начало дня
    end_datetime = datetime.combine(target_date, datetime.max.time())  # Конец дня

    tickets_sold = db.query(Ticket).filter(Ticket.sold == True,
                                           Ticket.sold_date >= start_datetime,
                                           Ticket.sold_date <= end_datetime).all()  # Проданные билеты за день
    total_revenue = sum(ticket.price for ticket in tickets_sold)  # Общая выручка

    film_revenue = {}  # Выручка по фильмам
    for ticket in tickets_sold:
        screening = db.query(Screening).filter(Screening.id == ticket.screening_id).first()
        if screening:
            film = db.query(Film).filter(Film.id == screening.film_id).first()
            if film:
                film_revenue[film.title] = film_revenue.get(film.title, 0) + ticket.price

    return {
        'date': target_date.isoformat(),
        'total_tickets_sold': len(tickets_sold),
        'total_revenue': round(total_revenue, 2),
        'average_ticket_price': round(total_revenue / len(tickets_sold), 2) if tickets_sold else 0,
        'revenue_by_film': film_revenue
    }


def get_screening_attendance(db: Session, screening_id: int) -> Dict[str, Any]:  # Получить посещаемость показа
    validate_positive_int(screening_id, "ID показа")  # Проверка ID
    screening = db.query(Screening).filter(Screening.id == screening_id).first()  # Поиск показа
    if not screening:
        raise ValueError(f"Показ с ID {screening_id} не найден")  # Ошибка

    all_tickets = db.query(Ticket).filter(Ticket.screening_id == screening_id).all()  # Все билеты
    sold_tickets = [t for t in all_tickets if t.sold]  # Проданные билеты
    film = db.query(Film).filter(Film.id == screening.film_id).first()  # Фильм

    return {
        'screening_id': screening_id,
        'film_title': film.title if film else "Неизвестно",
        'datetime': screening.datetime,
        'hall': screening.hall,
        'total_seats': len(all_tickets),
        'seats_sold': len(sold_tickets),
        'seats_available': len(all_tickets) - len(sold_tickets),
        'occupancy_rate': round(len(sold_tickets) / len(all_tickets) * 100, 2) if all_tickets else 0,
        'total_revenue': sum(t.price for t in sold_tickets),
        'sold_seat_numbers': [t.seat_number for t in sold_tickets]
    }


def get_popular_films(db: Session, limit: int = 5, days: int = 30) -> List[Dict[str, Any]]:  # Получить популярные фильмы
    validate_positive_int(limit, "limit")  # Проверка лимита
    validate_positive_int(days, "days")  # Проверка периода
    start_date = datetime.now() - timedelta(days=days)  # Начало периода

    results = db.query(Film.title,
                       func.count(Ticket.id).label('tickets_sold'),
                       func.sum(Ticket.price).label('total_revenue')).join(
        Screening, Film.id == Screening.film_id).join(
        Ticket, Screening.id == Ticket.screening_id).filter(
        Ticket.sold == True, Ticket.sold_date >= start_date).group_by(
        Film.id, Film.title).order_by(func.count(Ticket.id).desc()).limit(limit).all()  # Запрос

    popular_films = []  # Список результатов
    for idx, (title, tickets_sold, total_revenue) in enumerate(results):
        popular_films.append({
            'rank': idx + 1,
            'film_title': title,
            'tickets_sold': tickets_sold or 0,
            'total_revenue': round(float(total_revenue or 0), 2),
            'average_ticket_price': round(float(total_revenue or 0) / (tickets_sold or 1), 2)
        })
    return popular_films


def get_screenings_for_date(db: Session, date_str: str) -> List[Dict[str, Any]]:
    """Получить все показы на определенную дату"""
    target_date = parse_date(date_str)
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    screenings = db.query(Screening).filter(
        Screening.datetime >= start_datetime,
        Screening.datetime <= end_datetime
    ).order_by(Screening.datetime).all()

    result = []
    for screening in screenings:
        film = db.query(Film).filter(Film.id == screening.film_id).first()
        result.append({
            'id': screening.id,
            'film_title': film.title if film else f"Фильм ID:{screening.film_id}",
            'datetime': screening.datetime,
            'hall': screening.hall,
            'ticket_price': screening.ticket_price
        })

    return result
