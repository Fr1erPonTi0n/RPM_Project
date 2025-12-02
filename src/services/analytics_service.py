# ФУНКЦИЯ УПРАВЛЕНИЯ ORM-МОДЕЛИ С ПОМОЩЬЮ CRUD ДЛЯ:
# - АНАЛИТИКИ ЭФФЕКТИВНОСТИ ПОСТАВЩИКОВ
# - ФОРМИРОВАНИЕ АНАЛИЗОВ ДОХОДОВ И РАСХОДОВ КИНОТЕАТРА

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from models.analytics import SupplierKPI, Complaint


# ========== РАБОТА С ОЦЕНКАМИ ПОСТАВЩИКОВ ==========

def add_supplier_score(db: Session, supplier_id: int, amount_score: float, time_score: float, quality_score: float,
                       price_score: float) -> SupplierKPI:
    # СОЗДАТЬ НОВУЮ ОЦЕНКУ ДЛЯ ПОСТАВЩИКА

    # ВАЛИДАЦИЯ: ВСЕ ОЦЕНКИ ДОЛЖНЫ БЫТЬ ОТ 1.0 ДО 5.0 (FLOAT)
    all_scores = [amount_score, time_score, quality_score, price_score]
    for i, score in enumerate(all_scores):
        if not isinstance(score, (int, float)):
            raise TypeError(f"Оценка должна быть числом, получено: {type(score).__name__}")
        if not (1.0 <= float(score) <= 5.0):
            raise ValueError(f"Оценка должна быть от 1.0 до 5.0, получено: {score}")

    # ВАЛИДАЦИЯ: supplier_id ДОЛЖЕН БЫТЬ ПОЛОЖИТЕЛЬНЫМ ЦЕЛЫМ ЧИСЛОМ
    if not isinstance(supplier_id, int) or supplier_id <= 0:
        raise ValueError(f"ID поставщика должен быть положительным целым числом, получено: {supplier_id}")

    try:
        # ВЫЧИСЛЯЕМ ОБЩУЮ ОЦЕНКУ КАК СРЕДНЕЕ АРИФМЕТИЧЕСКОЕ
        total_score = (amount_score + time_score + quality_score + price_score) / 4
        total_score = round(total_score, 2)  # ОКРУГЛЯЕМ ДО 2 ЗНАКОВ

        new_score = SupplierKPI(
            supplier_id=supplier_id,
            count_score=amount_score,
            on_time_delivery=time_score,
            quantity_score=quality_score,
            budget_adherence=price_score,
            calculation_date=datetime.now(),
            overall_rating=total_score
        )

        db.add(new_score)
        db.commit()
        db.refresh(new_score)
        return new_score

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при создании оценки: {str(e)}")


def get_all_scores(db: Session, supplier_id: Optional[int] = None, limit: int = 100) -> List[SupplierKPI]:
    # ПОЛУЧИТЬ ВСЕ ОЦЕНКИ ПОСТАВЩИКОВ

    try:
        if not isinstance(limit, int):
            raise TypeError(f"Параметр limit должен быть целым числом, получено: {type(limit).__name__}")
        if limit <= 0:
            raise ValueError(f"Параметр limit должен быть положительным, получено: {limit}")

        query = db.query(SupplierKPI)

        if supplier_id is not None:
            if not isinstance(supplier_id, int):
                raise TypeError(f"ID поставщика должен быть целым числом, получено: {type(supplier_id).__name__}")
            if supplier_id <= 0:
                raise ValueError(f"ID поставщика должен быть положительным, получено: {supplier_id}")
            query = query.filter(SupplierKPI.supplier_id == supplier_id)

        return query.order_by(SupplierKPI.calculation_date.desc()).limit(limit).all()

    except (TypeError, ValueError) as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении оценок: {str(e)}")


def remove_score(db: Session, score_id: int) -> bool:
    # УДАЛИТЬ ОЦЕНКУ ПОСТАВЩИКА

    if not isinstance(score_id, int) or score_id <= 0:
        raise ValueError(f"ID оценки должен быть положительным целым числом, получено: {score_id}")

    try:
        score = db.query(SupplierKPI).filter(SupplierKPI.id == score_id).first()
        if not score:
            return False

        db.delete(score)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при удалении оценки: {str(e)}")


# ========== РАБОТА С ПРЕТЕНЗИЯМИ КЛИЕНТОВ ==========

def create_complaint(db: Session, description: str, order_id: Optional[int] = None,
                     ticket_id: Optional[int] = None) -> Complaint:
    # СОЗДАТЬ НОВУЮ ПРЕТЕНЗИЮ ОТ КЛИЕНТА

    # ВАЛИДАЦИЯ: ОПИСАНИЕ НЕ ДОЛЖНО БЫТЬ ПУСТЫМ
    if not description or not isinstance(description, str):
        raise ValueError("Описание претензии должно быть непустой строкой")
    if len(description.strip()) < 5:
        raise ValueError("Описание претензии должно содержать минимум 5 символов")

    # ВАЛИДАЦИЯ: ХОТЯ БЫ ОДИН ИЗ order_id ИЛИ ticket_id ДОЛЖЕН БЫТЬ УКАЗАН
    if order_id is None and ticket_id is None:
        raise ValueError("Должен быть указан order_id или ticket_id")

    # ВАЛИДАЦИЯ: order_id ЕСЛИ УКАЗАН
    if order_id is not None:
        if not isinstance(order_id, int) or order_id <= 0:
            raise ValueError(f"order_id должен быть положительным целым числом, получено: {order_id}")

    # ВАЛИДАЦИЯ: ticket_id ЕСЛИ УКАЗАН
    if ticket_id is not None:
        if not isinstance(ticket_id, int) or ticket_id <= 0:
            raise ValueError(f"ticket_id должен быть положительным целым числом, получено: {ticket_id}")

    try:
        new_complaint = Complaint(
            order_id=order_id,
            ticket_id=ticket_id,
            description=description.strip(),
            date=datetime.now(),
            status="на рассмотрении"
        )

        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)
        return new_complaint

    except ValueError as ve:
        db.rollback()
        raise ve
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при создании претензии: {str(e)}")


def get_all_complaints(db: Session, status: Optional[str] = None, limit: int = 100) -> List[Complaint]:
    # ПОЛУЧИТЬ ВСЕ ПРЕТЕНЗИИ

    try:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError(f"Параметр limit должен быть положительным целым числом, получено: {limit}")

        query = db.query(Complaint)

        # ВАЛИДАЦИЯ И ФИЛЬТРАЦИЯ ПО СТАТУСУ
        if status is not None:
            valid_statuses = ["на рассмотрении", "решён", "не решён"]
            if status not in valid_statuses:
                raise ValueError(f"Недопустимый статус. Допустимые значения: {valid_statuses}")
            query = query.filter(Complaint.status == status)

        return query.order_by(Complaint.date.desc()).limit(limit).all()

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Ошибка базы данных при получении претензий: {str(e)}")


def update_complaint_status(db: Session, complaint_id: int, new_status: str) -> Optional[Complaint]:
    # ОБНОВИТЬ СТАТУС ПРЕТЕНЗИИ

    if not isinstance(complaint_id, int) or complaint_id <= 0:
        raise ValueError(f"ID претензии должен быть положительным целым числом, получено: {complaint_id}")

    # ВАЛИДАЦИЯ: ПРОВЕРКА КОРРЕКТНОСТИ СТАТУСА
    valid_statuses = ["на рассмотрении", "решён", "не решён"]
    if new_status not in valid_statuses:
        raise ValueError(f"Недопустимый статус. Допустимые значения: {valid_statuses}")

    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return None

        complaint.status = new_status
        db.commit()
        db.refresh(complaint)
        return complaint

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при обновлении статуса претензии: {str(e)}")


def delete_complaint(db: Session, complaint_id: int) -> bool:
    # УДАЛИТЬ ПРЕТЕНЗИЮ

    if not isinstance(complaint_id, int) or complaint_id <= 0:
        raise ValueError(f"ID претензии должен быть положительным целым числом, получено: {complaint_id}")

    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return False

        db.delete(complaint)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка базы данных при удалении претензии: {str(e)}")


def get_complaint_stats(db: Session, days: int = 30) -> Dict[str, Any]:
    # ПОЛУЧИТЬ СТАТИСТИКУ ПО ПРЕТЕНЗИЯМ ЗА ПЕРИОД

    if not isinstance(days, int) or days <= 0:
        raise ValueError(f"Количество дней должно быть положительным целым числом, получено: {days}")

    try:
        start_date = datetime.now() - timedelta(days=days)

        # ОБЩЕЕ КОЛИЧЕСТВО ПРЕТЕНЗИЙ ЗА ПЕРИОД
        total_count = db.query(func.count(Complaint.id)).filter(
            Complaint.date >= start_date
        ).scalar() or 0

        # КОЛИЧЕСТВО ПО СТАТУСАМ
        status_counts = {}
        for status in ["на рассмотрении", "решён", "не решён"]:
            count = db.query(func.count(Complaint.id)).filter(
                Complaint.date >= start_date,
                Complaint.status == status
            ).scalar() or 0
            status_counts[status] = count

        # СРЕДНЕЕ ВРЕМЯ ОТКРЫТЫХ ПРЕТЕНЗИЙ (В ДНЯХ)
        avg_open_days = None
        open_complaints = db.query(Complaint).filter(
            Complaint.status == "на рассмотрении",
            Complaint.date >= start_date
        ).all()

        if open_complaints:
            total_days = sum([(datetime.now() - comp.date).days for comp in open_complaints])
            avg_open_days = round(total_days / len(open_complaints), 1)

        return {
            'period_days': days,
            'start_date': start_date.date(),
            'total_complaints': total_count,
            'by_status': status_counts,
            'avg_open_days': avg_open_days,
            'resolution_rate': round(status_counts['решён'] / total_count * 100, 1) if total_count > 0 else 0
        }

    except Exception as e:
        raise RuntimeError(f"Ошибка при получении статистики претензий: {str(e)}")


# ========== АНАЛИТИКА ЭФФЕКТИВНОСТИ ПОСТАВЩИКОВ ==========

def get_supplier_top(db: Session, days: int = 30, top_n: int = 10) -> List[Dict[str, Any]]:
    # ПОЛУЧИТЬ РЕЙТИНГ ПОСТАВЩИКОВ

    if not isinstance(days, int) or days <= 0:
        raise ValueError(f"Количество дней должно быть положительным целым числом, получено: {days}")

    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError(f"Количество поставщиков в топе должно быть положительным целым числом, получено: {top_n}")

    try:
        start_date = datetime.now() - timedelta(days=days)

        results = db.query(
            SupplierKPI.supplier_id,
            func.avg(SupplierKPI.overall_rating).label('avg_score'),
            func.avg(SupplierKPI.on_time_delivery).label('avg_time'),
            func.avg(SupplierKPI.quantity_score).label('avg_quality'),
            func.avg(SupplierKPI.budget_adherence).label('avg_price'),
            func.count(SupplierKPI.id).label('score_count')
        ).filter(
            SupplierKPI.calculation_date >= start_date
        ).group_by(
            SupplierKPI.supplier_id
        ).order_by(
            func.avg(SupplierKPI.overall_rating).desc()
        ).limit(top_n).all()

        formatted_results = []
        for idx, row in enumerate(results):
            supplier_data = {
                'rank': idx + 1,
                'supplier_id': row.supplier_id,
                'average_score': round(row.avg_score, 2),
                'average_time': round(row.avg_time, 2),
                'average_quality': round(row.avg_quality, 2),
                'average_price': round(row.avg_price, 2),
                'times_scored': row.score_count
            }
            formatted_results.append(supplier_data)

        return formatted_results

    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании рейтинга поставщиков: {str(e)}")


# ========== АНАЛИТИКА ДОХОДОВ И РАСХОДОВ ==========

def get_daily_money(db: Session, target_date: datetime) -> Dict[str, Any]:
    # ПОЛУЧИТЬ ОТЧЁТ О ДОХОДАХ И РАСХОДАХ ЗА ДЕНЬ

    if not isinstance(target_date, datetime):
        raise TypeError(f"Дата должна быть datetime объектом, получено: {type(target_date).__name__}")

    if target_date > datetime.now():
        raise ValueError("Дата отчёта не может быть в будущем")

    try:
        # ЗДЕСЬ БУДУТ РЕАЛЬНЫЕ SQL-ЗАПРОСЫ К БАЗЕ
        ticket_income = 150000
        snack_income = 50000
        total_income = ticket_income + snack_income

        staff_costs = 80000
        rent_costs = 40000
        product_costs = 60000
        total_costs = staff_costs + rent_costs + product_costs

        profit = total_income - total_costs

        return {
            'date': target_date.date(),
            'income': {
                'tickets': ticket_income,
                'snacks': snack_income,
                'total': total_income
            },
            'costs': {
                'staff': staff_costs,
                'rent': rent_costs,
                'products': product_costs,
                'total': total_costs
            },
            'profit': profit,
            'profit_margin': round(profit / total_income * 100, 2) if total_income > 0 else 0
        }

    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании дневного отчёта: {str(e)}")


def get_period_money(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    # ПОЛУЧИТЬ ОТЧЁТ О ДОХОДАХ И РАСХОДАХ ЗА ПЕРИОД

    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise TypeError("Даты начала и окончания должны быть datetime объектами")

    if start_date > end_date:
        raise ValueError("Дата начала периода не может быть позже даты окончания")

    if end_date > datetime.now():
        raise ValueError("Дата окончания периода не может быть в будущем")

    try:
        days_count = (end_date - start_date).days + 1

        if days_count <= 0:
            raise ValueError("Некорректный период: количество дней должно быть положительным")

        # ВРЕМЕННЫЕ ДАННЫЕ
        total_income = 1200000
        total_costs = 900000
        total_profit = total_income - total_costs

        avg_daily_income = total_income / days_count
        avg_daily_profit = total_profit / days_count

        return {
            'period': {
                'start': start_date.date(),
                'end': end_date.date(),
                'days': days_count
            },
            'totals': {
                'income': total_income,
                'costs': total_costs,
                'profit': total_profit
            },
            'averages': {
                'daily_income': round(avg_daily_income, 2),
                'daily_profit': round(avg_daily_profit, 2)
            },
            'profit_margin': round(total_profit / total_income * 100, 2) if total_income > 0 else 0
        }

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании отчёта за период: {str(e)}")

