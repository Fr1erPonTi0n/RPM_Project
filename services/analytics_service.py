from sqlalchemy.orm import Session  # Импортируем сессию SQLAlchemy
from sqlalchemy import func  # Импорт агрегатных функций SQLAlchemy
from datetime import datetime, timedelta  # Работа с датами и интервалами
from typing import List, Optional, Dict, Any  # Типизация для удобства
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.analytics import SupplierKPI, Complaint  # Импортируем ORM-модели
from utils.validators import validate_positive_int, validate_status, validate_limit

# ОЦЕНКИ ПОСТАВЩИКОВ
def add_supplier_score(db: Session, supplier_id: int,
                       amount_score: float, time_score: float,
                       quality_score: float, price_score: float) -> SupplierKPI:  # Добавить оценку поставщика
    validate_positive_int(supplier_id, "ID поставщика")  # Проверяем ID поставщика
    scores = [amount_score, time_score, quality_score, price_score]  # Собираем все оценки
    if not all(isinstance(s, (int, float)) and 1.0 <= float(s) <= 5.0 for s in scores):  # Проверяем тип и диапазон
        raise ValueError("Все оценки должны быть числами от 1.0 до 5.0")  # Бросаем ошибку, если недопустимо
    total_score = round(sum(scores) / 4, 2)  # Считаем среднюю оценку и округляем до двух знаков

    new_score = SupplierKPI(  # Создаём новый ORM-объект оценки
        supplier_id=supplier_id,
        count_score=amount_score,
        on_time_delivery=time_score,
        quantity_score=quality_score,
        budget_adherence=price_score,
        calculation_date=datetime.now(),
        overall_rating=total_score
    )

    with db.begin():  # Начинаем транзакцию
        db.add(new_score)  # Добавляем запись в сессию
    db.refresh(new_score)  # Обновляем объект из базы
    return new_score  # Возвращаем созданную запись


def get_all_scores(db: Session, supplier_id: Optional[int] = None, limit: int = 100) -> List[SupplierKPI]:  # Получить оценки
    validate_limit(limit)  # Проверяем лимит
    query = db.query(SupplierKPI)  # Формируем базовый запрос
    if supplier_id is not None:  # Если указан фильтр по поставщику
        validate_positive_int(supplier_id, "ID поставщика")  # Проверяем корректность ID
        query = query.filter(SupplierKPI.supplier_id == supplier_id)  # Применяем фильтр по поставщику
    return query.order_by(SupplierKPI.calculation_date.desc()).limit(limit).all()  # Сортируем, ограничиваем, выбираем


def remove_score(db: Session, score_id: int) -> bool:  # Удалить оценку поставщика по ID
    validate_positive_int(score_id, "ID оценки")  # Проверяем ID оценки
    score = db.query(SupplierKPI).filter_by(id=score_id).first()  # Ищем запись по ID
    if not score:  # Если запись не найдена
        return False  # Возвращаем False (ничего не удалено)
    with db.begin():  # Начинаем транзакцию
        db.delete(score)  # Удаляем найденную запись
    return True  # Возвращаем успех


# ПРЕТЕНЗИИ КЛИЕНТОВ

def create_complaint(db: Session, description: str,
                     order_id: Optional[int] = None,
                     ticket_id: Optional[int] = None) -> Complaint:  # Создать претензию клиента
    if not description or len(description.strip()) < 5:  # Проверяем описание на минимальную длину
        raise ValueError("Описание претензии должно содержать минимум 5 символов")  # Бросаем ошибку
    if order_id is None and ticket_id is None:  # Должен быть указан хотя бы один идентификатор
        raise ValueError("Нужно указать order_id или ticket_id")  # Бросаем ошибку
    if order_id is not None:  # Если указан order_id
        validate_positive_int(order_id, "order_id")  # Проверяем корректность order_id
    if ticket_id is not None:  # Если указан ticket_id
        validate_positive_int(ticket_id, "ticket_id")  # Проверяем корректность ticket_id

    new_complaint = Complaint(  # Создаём ORM-объект претензии
        order_id=order_id,
        ticket_id=ticket_id,
        description=description.strip(),
        date=datetime.now(),
        status="на рассмотрении"
    )

    with db.begin():  # Начинаем транзакцию
        db.add(new_complaint)  # Добавляем претензию
    db.refresh(new_complaint)  # Обновляем объект из базы
    return new_complaint  # Возвращаем созданную запись


def get_all_complaints(db: Session, status: Optional[str] = None, limit: int = 100) -> List[Complaint]:  # Получить претензии
    validate_limit(limit)  # Проверяем лимит
    query = db.query(Complaint)  # Формируем базовый запрос
    if status:  # Если указан фильтр по статусу
        validate_status(status)  # Проверяем допустимость статуса
        query = query.filter(Complaint.status == status)  # Применяем фильтр по статусу
    return query.order_by(Complaint.date.desc()).limit(limit).all()  # Сортируем, ограничиваем, выбираем


def update_complaint_status(db: Session, complaint_id: int, new_status: str) -> Optional[Complaint]:  # Обновить статус претензии
    validate_positive_int(complaint_id, "ID претензии")  # Проверяем ID претензии
    validate_status(new_status)  # Проверяем новый статус

    complaint = db.query(Complaint).filter_by(id=complaint_id).first()  # Ищем претензию по ID
    if not complaint:  # Если не найдена
        return None  # Возвращаем None (ничего не обновлено)

    complaint.status = new_status  # Присваиваем новый статус
    with db.begin():  # Начинаем транзакцию
        db.add(complaint)  # Фиксируем изменение
    db.refresh(complaint)  # Обновляем объект из базы
    return complaint  # Возвращаем обновлённую запись


def delete_complaint(db: Session, complaint_id: int) -> bool:  # Удалить претензию по ID
    validate_positive_int(complaint_id, "ID претензии")  # Проверяем ID претензии
    complaint = db.query(Complaint).filter_by(id=complaint_id).first()  # Ищем запись по ID
    if not complaint:  # Если запись не найдена
        return False  # Возвращаем False (ничего не удалено)
    with db.begin():  # Начинаем транзакцию
        db.delete(complaint)  # Удаляем найденную запись
    return True  # Возвращаем успех


def get_complaint_stats(db: Session, days: int = 30) -> Dict[str, Any]:  # Сформировать статистику по претензиям за период
    validate_positive_int(days, "Количество дней")  # Проверяем число дней
    start_date = datetime.now() - timedelta(days=days)  # Вычисляем дату начала периода

    total_count = db.query(func.count(Complaint.id)).filter(Complaint.date >= start_date).scalar() or 0  # Общее число претензий
    status_counts = {s: db.query(func.count(Complaint.id)).filter(Complaint.date >= start_date, Complaint.status == s).scalar() or 0
                     for s in ["на рассмотрении", "решён", "не решён"]}  # Количество по каждому статусу

    avg_open_days = None  # Среднее время открытых претензий (в днях)
    open_complaints = db.query(Complaint).filter(Complaint.status == "на рассмотрении", Complaint.date >= start_date).all()  # Выборка открытых
    if open_complaints:  # Если есть открытые претензии
        total_days = sum((datetime.now() - comp.date).days for comp in open_complaints)  # Суммируем дни в открытом состоянии
        avg_open_days = round(total_days / len(open_complaints), 1)  # Считаем среднее и округляем

    return {  # Возвращаем итоговую статистику
        'period_days': days,
        'start_date': start_date.date(),
        'total_complaints': total_count,
        'by_status': status_counts,
        'avg_open_days': avg_open_days,
        'resolution_rate': round(status_counts['решён'] / total_count * 100, 1) if total_count else 0
    }


# АНАЛИТИКА ЭФФЕКТИВНОСТИ ПОСТАВЩИКОВ

def get_supplier_top(db: Session, days: int = 30, top_n: int = 10) -> List[Dict[str, Any]]:  # Получить рейтинг поставщиков за период
    validate_positive_int(days, "Количество дней")  # Проверяем число дней
    validate_positive_int(top_n, "Количество поставщиков в топе")  # Проверяем размер топа
    start_date = datetime.now() - timedelta(days=days)  # Вычисляем дату начала периода

    results = db.query(  # Формируем агрегирующий запрос
        SupplierKPI.supplier_id,
        func.avg(SupplierKPI.overall_rating).label('avg_score'),
        func.avg(SupplierKPI.on_time_delivery).label('avg_time'),
        func.avg(SupplierKPI.quantity_score).label('avg_quality'),
        func.avg(SupplierKPI.budget_adherence).label('avg_price'),
        func.count(SupplierKPI.id).label('score_count')
    ).filter(
        SupplierKPI.calculation_date >= start_date  # Ограничиваем периодом
    ).group_by(
        SupplierKPI.supplier_id  # Группируем по поставщику
    ).order_by(
        func.avg(SupplierKPI.overall_rating).desc()  # Сортируем по средней общей оценке
    ).limit(top_n).all()  # Ограничиваем топ N

    return [{  # Форматируем результат в список словарей
        'rank': idx + 1,
        'supplier_id': row.supplier_id,
        'average_score': round(row.avg_score, 2),
        'average_time': round(row.avg_time, 2),
        'average_quality': round(row.avg_quality, 2),
        'average_price': round(row.avg_price, 2),
        'times_scored': row.score_count
    } for idx, row in enumerate(results)]  # Нумеруем позиции рейтинга

