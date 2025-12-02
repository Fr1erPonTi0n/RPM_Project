# ФУНКЦИЯ УПРАВЛЕНИЯ ORM-МОДЕЛИ С ПОМОЩЬЮ CRUD ДЛЯ: 
# - КИНОТЕАТРА

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import models.cinema as models


# ========== РАБОТА С ФИЛЬМАМИ ==========

def create_film(db: Session, license_id: int, title: str, duration: int, description: str = "") -> models.Film:
    # СОЗДАТЬ НОВЫЙ ФИЛЬМ

    # ВАЛИДАЦИЯ: license_id ДОЛЖЕН БЫТЬ ПОЛОЖИТЕЛЬНЫМ
    if not isinstance(license_id, int) or license_id <= 0:
        raise ValueError(f"ID лицензии должен быть положительным целым числом, получено: {license_id}")

    # ВАЛИДАЦИЯ: title НЕ ДОЛЖЕН БЫТЬ ПУСТЫМ
    if not title or not isinstance(title, str):
        raise ValueError("Название фильма должно быть непустой строкой")
    if len(title.strip()) < 1:
        raise ValueError("Название фильма должно содержать минимум 1 символ")

    # ВАЛИДАЦИЯ: duration ДОЛЖЕН БЫТЬ ПОЛОЖИТЕЛЬНЫМ
    if not isinstance(duration, int) or duration <= 0:
        raise ValueError(f"Длительность фильма должна быть положительным целым числом, получено: {duration}")

    # ВАЛИДАЦИЯ: МАКСИМАЛЬНАЯ ДЛИТЕЛЬНОСТЬ 300 МИНУТ (5 ЧАСОВ)
    if duration > 300:
        raise ValueError(f"Длительность фильма не может превышать 300 минут, получено: {duration}")

    try:
        # ПРОВЕРЯЕМ, НЕТ ЛИ УЖЕ ФИЛЬМА С ТАКИМ НАЗВАНИЕМ
        existing_film = db.query(models.Film).filter(func.lower(models.Film.title) == func.lower(title)).first()
        if existing_film:
            raise ValueError(f"Фильм с названием '{title}' уже существует (ID: {existing_film.id})")

        new_film = models.Film(
            license_id=license_id,
            title=title.strip(),
            duration=duration,
            description=description.strip() if description else ""
        )

        db.add(new_film)
        db.commit()
        db.refresh(new_film)
        return new_film

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при создании фильма: {str(e)}")


def get_all_films(db: Session, active_only: bool = False) -> List[models.Film]:
    # ПОЛУЧИТЬ ВСЕ ФИЛЬМЫ

    try:
        query = db.query(models.Film)

        # ЕСЛИ НУЖНЫ ТОЛЬКО АКТИВНЫЕ ФИЛЬМЫ (С ЗАПЛАНИРОВАННЫМИ ПОКАЗАМИ)
        if active_only:
            # ФИЛЬТРУЕМ ФИЛЬМЫ, У КОТОРЫХ ЕСТЬ БУДУЩИЕ ПОКАЗЫ
            current_time = datetime.now()
            query = query.join(models.Screening).filter(models.Screening.datetime > current_time)

        return query.order_by(models.Film.title).all()

    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении фильмов: {str(e)}")


def get_film_by_id(db: Session, film_id: int) -> Optional[models.Film]:
    # ПОЛУЧИТЬ ФИЛЬМ ПО ID

    if not isinstance(film_id, int) or film_id <= 0:
        raise ValueError(f"ID фильма должен быть положительным целым числом, получено: {film_id}")

    try:
        return db.query(models.Film).filter(models.Film.id == film_id).first()
    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении фильма: {str(e)}")


def update_film(db: Session, film_id: int, title: Optional[str] = None,
                duration: Optional[int] = None, description: Optional[str] = None) -> Optional[models.Film]:
    # ОБНОВИТЬ ИНФОРМАЦИЮ О ФИЛЬМЕ

    if not isinstance(film_id, int) or film_id <= 0:
        raise ValueError(f"ID фильма должен быть положительным целым числом, получено: {film_id}")

    try:
        film = db.query(models.Film).filter(models.Film.id == film_id).first()
        if not film:
            return None

        # ВАЛИДАЦИЯ И ОБНОВЛЕНИЕ title
        if title is not None:
            if not isinstance(title, str) or len(title.strip()) < 1:
                raise ValueError("Название фильма должно быть непустой строкой")
            film.title = title.strip()

        # ВАЛИДАЦИЯ И ОБНОВЛЕНИЕ duration
        if duration is not None:
            if not isinstance(duration, int) or duration <= 0:
                raise ValueError(f"Длительность фильма должна быть положительным целым числом, получено: {duration}")
            if duration > 300:
                raise ValueError(f"Длительность фильма не может превышать 300 минут, получено: {duration}")
            film.duration = duration

        # ОБНОВЛЕНИЕ description
        if description is not None:
            film.description = description.strip() if description else ""

        db.commit()
        db.refresh(film)
        return film

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при обновлении фильма: {str(e)}")


def delete_film(db: Session, film_id: int) -> bool:
    # УДАЛИТЬ ФИЛЬМ

    if not isinstance(film_id, int) or film_id <= 0:
        raise ValueError(f"ID фильма должен быть положительным целым числом, получено: {film_id}")

    try:
        film = db.query(models.Film).filter(models.Film.id == film_id).first()
        if not film:
            return False

        # ПРОВЕРЯЕМ, ЕСТЬ ЛИ ЗАПЛАНИРОВАННЫЕ ПОКАЗЫ У ЭТОГО ФИЛЬМА
        future_screenings = db.query(models.Screening).filter(
            models.Screening.film_id == film_id,
            models.Screening.datetime > datetime.now()
        ).count()

        if future_screenings > 0:
            raise ValueError(f"Невозможно удалить фильм: есть {future_screenings} запланированных показов")

        db.delete(film)
        db.commit()
        return True

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при удалении фильма: {str(e)}")


# ========== РАБОТА С ПОКАЗАМИ ФИЛЬМОВ ==========

def create_screening(db: Session, film_id: int, datetime_str: str, hall: str, ticket_price: float) -> models.Screening:
    # СОЗДАТЬ НОВЫЙ ПОКАЗ ФИЛЬМА

    # ВАЛИДАЦИЯ: film_id
    if not isinstance(film_id, int) or film_id <= 0:
        raise ValueError(f"ID фильма должен быть положительным целым числом, получено: {film_id}")

    # ВАЛИДАЦИЯ: datetime
    try:
        screening_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(
            f"Некорректный формат даты и времени: {datetime_str}. Используйте формат ISO (YYYY-MM-DDTHH:MM:SS)")

    # ВАЛИДАЦИЯ: ДАТА НЕ ДОЛЖНА БЫТЬ В ПРОШЛОМ
    if screening_datetime < datetime.now():
        raise ValueError("Дата и время показа не могут быть в прошлом")

    # ВАЛИДАЦИЯ: hall
    if not hall or not isinstance(hall, str):
        raise ValueError("Название зала должно быть непустой строкой")

    # ВАЛИДАЦИЯ: ticket_price
    if not isinstance(ticket_price, (int, float)) or ticket_price <= 0:
        raise ValueError(f"Цена билета должна быть положительным числом, получено: {ticket_price}")

    try:
        # ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ ФИЛЬМА
        film = db.query(models.Film).filter(models.Film.id == film_id).first()
        if not film:
            raise ValueError(f"Фильм с ID {film_id} не найден")

        # ПРОВЕРЯЕМ, НЕТ ЛИ КОНФЛИКТА ВРЕМЕНИ В ТОМ ЖЕ ЗАЛЕ
        # ВРЕМЯ ОКОНЧАНИЯ ПОКАЗА = ВРЕМЯ НАЧАЛА + ДЛИТЕЛЬНОСТЬ ФИЛЬМА
        screening_end = screening_datetime + timedelta(minutes=film.duration)

        conflicting_screening = db.query(models.Screening).filter(
            models.Screening.hall == hall,
            and_(
                models.Screening.datetime < screening_end,
                func.datetime(models.Screening.datetime, f'+{film.duration} minutes') > screening_datetime
            )
        ).first()

        if conflicting_screening:
            raise ValueError(f"Конфликт времени в зале '{hall}'. Уже есть показ с {conflicting_screening.datetime}")

        new_screening = models.Screening(
            film_id=film_id,
            datetime=screening_datetime,
            hall=hall.strip(),
            ticket_price=round(float(ticket_price), 2)
        )

        db.add(new_screening)
        db.commit()
        db.refresh(new_screening)
        return new_screening

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при создании показа: {str(e)}")


def get_all_screenings(db: Session, film_id: Optional[int] = None,
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[models.Screening]:
    # ПОЛУЧИТЬ ВСЕ ПОКАЗЫ С ФИЛЬТРАЦИЕЙ

    try:
        query = db.query(models.Screening)

        # ФИЛЬТРАЦИЯ ПО film_id
        if film_id is not None:
            if not isinstance(film_id, int) or film_id <= 0:
                raise ValueError(f"ID фильма должен быть положительным целым числом, получено: {film_id}")
            query = query.filter(models.Screening.film_id == film_id)

        # ФИЛЬТРАЦИЯ ПО ДАТАМ
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(models.Screening.datetime >= start)
            except ValueError:
                raise ValueError(f"Некорректный формат начальной даты: {start_date}")

        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(models.Screening.datetime <= end)
            except ValueError:
                raise ValueError(f"Некорректный формат конечной даты: {end_date}")

        return query.order_by(models.Screening.datetime).all()

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении показов: {str(e)}")


def get_available_screenings(db: Session) -> List[Dict[str, Any]]:
    # ПОЛУЧИТЬ ДОСТУПНЫЕ ДЛЯ ПОКУПКИ ПОКАЗЫ (БУДУЩИЕ ПОКАЗЫ)

    try:
        current_time = datetime.now()

        results = db.query(
            models.Screening,
            models.Film.title,
            models.Film.duration
        ).join(
            models.Film, models.Screening.film_id == models.Film.id
        ).filter(
            models.Screening.datetime > current_time
        ).order_by(
            models.Screening.datetime
        ).all()

        screenings_list = []
        for screening, film_title, film_duration in results:
            screenings_list.append({
                'screening_id': screening.id,
                'film_title': film_title,
                'datetime': screening.datetime,
                'hall': screening.hall,
                'ticket_price': screening.ticket_price,
                'duration_minutes': film_duration,
                'end_time': screening.datetime + timedelta(minutes=film_duration)
            })

        return screenings_list

    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении доступных показов: {str(e)}")


def update_screening(db: Session, screening_id: int, datetime_str: Optional[str] = None,
                     hall: Optional[str] = None, ticket_price: Optional[float] = None) -> Optional[models.Screening]:
    # ОБНОВИТЬ ИНФОРМАЦИЮ О ПОКАЗЕ

    if not isinstance(screening_id, int) or screening_id <= 0:
        raise ValueError(f"ID показа должен быть положительным целым числом, получено: {screening_id}")

    try:
        screening = db.query(models.Screening).filter(models.Screening.id == screening_id).first()
        if not screening:
            return None

        # ПРОВЕРЯЕМ, НЕ ПРОШЕЛ ЛИ УЖЕ ПОКАЗ
        if screening.datetime < datetime.now():
            raise ValueError("Невозможно изменить информацию о прошедшем показе")

        # ОБНОВЛЕНИЕ datetime
        if datetime_str is not None:
            try:
                new_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                if new_datetime < datetime.now():
                    raise ValueError("Новая дата и время показа не могут быть в прошлом")
                screening.datetime = new_datetime
            except ValueError:
                raise ValueError(f"Некорректный формат даты и времени: {datetime_str}")

        # ОБНОВЛЕНИЕ hall
        if hall is not None:
            if not hall or not isinstance(hall, str):
                raise ValueError("Название зала должно быть непустой строкой")
            screening.hall = hall.strip()

        # ОБНОВЛЕНИЕ ticket_price
        if ticket_price is not None:
            if not isinstance(ticket_price, (int, float)) or ticket_price <= 0:
                raise ValueError(f"Цена билета должна быть положительным числом, получено: {ticket_price}")
            screening.ticket_price = round(float(ticket_price), 2)

        db.commit()
        db.refresh(screening)
        return screening

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при обновлении показа: {str(e)}")


def delete_screening(db: Session, screening_id: int) -> bool:
    # УДАЛИТЬ ПОКАЗ

    if not isinstance(screening_id, int) or screening_id <= 0:
        raise ValueError(f"ID показа должен быть положительным целым числом, получено: {screening_id}")

    try:
        screening = db.query(models.Screening).filter(models.Screening.id == screening_id).first()
        if not screening:
            return False

        # ПРОВЕРЯЕМ, НЕ ПРОШЕЛ ЛИ УЖЕ ПОКАЗ
        if screening.datetime < datetime.now():
            raise ValueError("Невозможно удалить прошедший показ")

        # ПРОВЕРЯЕМ, ЕСТЬ ЛИ ПРОДАННЫЕ БИЛЕТЫ НА ЭТОТ ПОКАЗ
        sold_tickets = db.query(models.Ticket).filter(
            models.Ticket.screening_id == screening_id,
            models.Ticket.sold == True
        ).count()

        if sold_tickets > 0:
            raise ValueError(f"Невозможно удалить показ: продано {sold_tickets} билетов")

        db.delete(screening)
        db.commit()
        return True

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при удалении показа: {str(e)}")


# ========== РАБОТА С БИЛЕТАМИ ==========

def create_ticket(db: Session, screening_id: int, seat_number: str, price: float) -> models.Ticket:
    # СОЗДАТЬ НОВЫЙ БИЛЕТ

    # ВАЛИДАЦИЯ: screening_id
    if not isinstance(screening_id, int) or screening_id <= 0:
        raise ValueError(f"ID показа должен быть положительным целым числом, получено: {screening_id}")

    # ВАЛИДАЦИЯ: seat_number
    if not seat_number or not isinstance(seat_number, str):
        raise ValueError("Номер места должен быть непустой строкой")

    # ВАЛИДАЦИЯ: price
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Цена билета должна быть положительным числом, получено: {price}")

    try:
        # ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ ПОКАЗА
        screening = db.query(models.Screening).filter(models.Screening.id == screening_id).first()
        if not screening:
            raise ValueError(f"Показ с ID {screening_id} не найден")

        # ПРОВЕРЯЕМ, НЕ ПРОШЕЛ ЛИ УЖЕ ПОКАЗ
        if screening.datetime < datetime.now():
            raise ValueError("Невозможно создать билет на прошедший показ")

        # ПРОВЕРЯЕМ, НЕ ЗАНЯТО ЛИ МЕСТО
        existing_ticket = db.query(models.Ticket).filter(
            models.Ticket.screening_id == screening_id,
            models.Ticket.seat_number == seat_number.strip()
        ).first()

        if existing_ticket:
            if existing_ticket.sold:
                raise ValueError(f"Место {seat_number} уже продано")
            else:
                raise ValueError(f"Место {seat_number} уже существует (билет ID: {existing_ticket.id})")

        new_ticket = models.Ticket(
            screening_id=screening_id,
            seat_number=seat_number.strip(),
            price=round(float(price), 2),
            sold=False,
            sold_date=None
        )

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при создании билета: {str(e)}")


def get_tickets_by_screening(db: Session, screening_id: int, sold_only: Optional[bool] = None) -> List[models.Ticket]:
    # ПОЛУЧИТЬ БИЛЕТЫ ПО ПОКАЗУ

    if not isinstance(screening_id, int) or screening_id <= 0:
        raise ValueError(f"ID показа должен быть положительным целым числом, получено: {screening_id}")

    try:
        query = db.query(models.Ticket).filter(models.Ticket.screening_id == screening_id)

        if sold_only is not None:
            query = query.filter(models.Ticket.sold == sold_only)

        return query.order_by(models.Ticket.seat_number).all()

    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении билетов: {str(e)}")


def get_available_seats(db: Session, screening_id: int) -> List[str]:
    # ПОЛУЧИТЬ СПИСОК СВОБОДНЫХ МЕСТ НА ПОКАЗ

    if not isinstance(screening_id, int) or screening_id <= 0:
        raise ValueError(f"ID показа должен быть положительным целым числом, получено: {screening_id}")

    try:
        # ВСЕ МЕСТА ДЛЯ ЭТОГО ПОКАЗА
        all_tickets = db.query(models.Ticket).filter(
            models.Ticket.screening_id == screening_id
        ).all()

        # НЕПРОДАННЫЕ МЕСТА
        available_seats = [ticket.seat_number for ticket in all_tickets if not ticket.sold]

        return available_seats

    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении свободных мест: {str(e)}")


def sell_ticket(db: Session, ticket_id: int, order_id: Optional[int] = None) -> Optional[models.Ticket]:
    # ПРОДАТЬ БИЛЕТ

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError(f"ID билета должен быть положительным целым числом, получено: {ticket_id}")

    if order_id is not None and (not isinstance(order_id, int) or order_id <= 0):
        raise ValueError(f"ID заказа должен быть положительным целым числом, получено: {order_id}")

    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if not ticket:
            return None

        # ПРОВЕРЯЕМ, НЕ ПРОДАН ЛИ УЖЕ БИЛЕТ
        if ticket.sold:
            raise ValueError(f"Билет ID {ticket_id} уже продан")

        # ПРОВЕРЯЕМ, НЕ ПРОШЕЛ ЛИ УЖЕ ПОКАЗ
        screening = db.query(models.Screening).filter(models.Screening.id == ticket.screening_id).first()
        if screening and screening.datetime < datetime.now():
            raise ValueError("Невозможно продать билет на прошедший показ")

        ticket.sold = True
        ticket.sold_date = datetime.now()
        if order_id:
            ticket.order_id = order_id

        db.commit()
        db.refresh(ticket)
        return ticket

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при продаже билета: {str(e)}")


def cancel_ticket_sale(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    # ОТМЕНИТЬ ПРОДАЖУ БИЛЕТА (ВОЗВРАТ)

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError(f"ID билета должен быть положительным целым числом, получено: {ticket_id}")

    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if not ticket:
            return None

        # ПРОВЕРЯЕМ, ПРОДАН ЛИ БИЛЕТ
        if not ticket.sold:
            raise ValueError(f"Билет ID {ticket_id} не продан, отмена невозможна")

        # ПРОВЕРЯЕМ, НЕ ПРОШЕЛ ЛИ УЖЕ ПОКАЗ
        screening = db.query(models.Screening).filter(models.Screening.id == ticket.screening_id).first()
        if screening and screening.datetime < datetime.now():
            raise ValueError("Невозможно отменить продажу билета на прошедший показ")

        ticket.sold = False
        ticket.sold_date = None
        ticket.order_id = None

        db.commit()
        db.refresh(ticket)
        return ticket

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при отмене продажи билета: {str(e)}")


def delete_ticket(db: Session, ticket_id: int) -> bool:
    # УДАЛИТЬ БИЛЕТ

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError(f"ID билета должен быть положительным целым числом, получено: {ticket_id}")

    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if not ticket:
            return False

        # ПРОВЕРЯЕМ, НЕ ПРОДАН ЛИ БИЛЕТ
        if ticket.sold:
            raise ValueError(f"Невозможно удалить проданный билет (ID: {ticket_id})")

        db.delete(ticket)
        db.commit()
        return True

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при удалении билета: {str(e)}")


# ========== АНАЛИТИКА КИНОТЕАТРА ==========

def get_daily_revenue(db: Session, date_str: str) -> Dict[str, Any]:
    # ПОЛУЧИТЬ ВЫРУЧКУ ЗА ДЕНЬ

    try:
        target_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except ValueError:
        raise ValueError(f"Некорректный формат даты: {date_str}. Используйте формат YYYY-MM-DD")

    try:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        # СЧИТАЕМ ПРОДАННЫЕ БИЛЕТЫ ЗА ДЕНЬ
        tickets_sold = db.query(models.Ticket).filter(
            models.Ticket.sold == True,
            models.Ticket.sold_date >= start_datetime,
            models.Ticket.sold_date <= end_datetime
        ).all()

        total_revenue = sum(ticket.price for ticket in tickets_sold)

        # ГРУППИРУЕМ ПО ФИЛЬМАМ
        film_revenue = {}
        for ticket in tickets_sold:
            screening = db.query(models.Screening).filter(models.Screening.id == ticket.screening_id).first()
            if screening:
                film = db.query(models.Film).filter(models.Film.id == screening.film_id).first()
                if film:
                    film_revenue[film.title] = film_revenue.get(film.title, 0) + ticket.price

        return {
            'date': target_date.isoformat(),
            'total_tickets_sold': len(tickets_sold),
            'total_revenue': round(total_revenue, 2),
            'average_ticket_price': round(total_revenue / len(tickets_sold), 2) if tickets_sold else 0,
            'revenue_by_film': film_revenue
        }

    except Exception as e:
        raise RuntimeError(f"Ошибка при расчете выручки: {str(e)}")


def get_screening_attendance(db: Session, screening_id: int) -> Dict[str, Any]:
    # ПОЛУЧИТЬ ИНФОРМАЦИЮ О ПОСЕЩАЕМОСТИ ПОКАЗА

    if not isinstance(screening_id, int) or screening_id <= 0:
        raise ValueError(f"ID показа должен быть положительным целым числом, получено: {screening_id}")

    try:
        screening = db.query(models.Screening).filter(models.Screening.id == screening_id).first()
        if not screening:
            raise ValueError(f"Показ с ID {screening_id} не найден")

        # ВСЕ БИЛЕТЫ НА ЭТОТ ПОКАЗ
        all_tickets = db.query(models.Ticket).filter(models.Ticket.screening_id == screening_id).all()

        # ПРОДАННЫЕ БИЛЕТЫ
        sold_tickets = [t for t in all_tickets if t.sold]

        film = db.query(models.Film).filter(models.Film.id == screening.film_id).first()

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

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении информации о посещаемости: {str(e)}")


def get_popular_films(db: Session, limit: int = 5, days: int = 30) -> List[Dict[str, Any]]:
    # ПОЛУЧИТЬ САМЫЕ ПОПУЛЯРНЫЕ ФИЛЬМЫ

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError(f"Параметр limit должен быть положительным целым числом, получено: {limit}")

    if not isinstance(days, int) or days <= 0:
        raise ValueError(f"Параметр days должен быть положительным целым числом, получено: {days}")

    try:
        start_date = datetime.now() - timedelta(days=days)

        # СЧИТАЕМ ПРОДАННЫЕ БИЛЕТЫ ПО ФИЛЬМАМ ЗА ПЕРИОД
        results = db.query(
            models.Film.title,
            func.count(models.Ticket.id).label('tickets_sold'),
            func.sum(models.Ticket.price).label('total_revenue')
        ).join(
            models.Screening, models.Film.id == models.Screening.film_id
        ).join(
            models.Ticket, models.Screening.id == models.Ticket.screening_id
        ).filter(
            models.Ticket.sold == True,
            models.Ticket.sold_date >= start_date
        ).group_by(
            models.Film.id, models.Film.title
        ).order_by(
            func.count(models.Ticket.id).desc()
        ).limit(limit).all()

        popular_films = []
        for idx, (title, tickets_sold, total_revenue) in enumerate(results):
            popular_films.append({
                'rank': idx + 1,
                'film_title': title,
                'tickets_sold': tickets_sold or 0,
                'total_revenue': round(float(total_revenue or 0), 2),
                'average_ticket_price': round(float(total_revenue or 0) / (tickets_sold or 1), 2)
            })

        return popular_films

    except Exception as e:
        raise RuntimeError(f"Ошибка при получении популярных фильмов: {str(e)}")
