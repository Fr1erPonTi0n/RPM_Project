# ORM МОДЕЛЬ ДЛЯ: 
# - АНАЛИТИКИ ЭФФЕКТИВНОСТИ ПОСТАВЩИКОВ
# - УПРАВЛЕНИЕ ПРЕТЕНЗИЯМИ ОТ КЛИЕНТОВ

from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base

class SupplierKPI(Base):
    # СРАВНИТЕЛЬНАЯ ТАБЛИЦА ПОСТАВЩИКОВ ПРОДУКЦИИ
    __tablename__ = 'supplier_kpis'

    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id')) # ПОСТАВЩИК
    count_score = Column(Float) # ОЦЕНКА КОЛИЧЕСТВА ПРОДУКЦИИ
    on_time_delivery = Column(Float) # СВОЕВРЕМЕННАЯ ДОСТАВКА
    quantity_score = Column(Float) # ОЦЕНКА КАЧЕСТВА ПРОДУКЦИИ
    budget_adherence = Column(Float) # СОБЛЮДЕНИЕ БЮДЖЕТА
    calculation_date = Column(DateTime) # ВРЕМЯ РАСЧЁТА
    overall_rating = Column(Float) # ОБЩАЯ ОЦЕНКА (СРЕДНЕЕ АРИФМЕТИЧЕСКОЕ)

    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    supplier = relationship("Supplier", back_populates="kpi") # ПРИВЯЗКА ПОСТАВЩИКА К ORM МОДЕЛИ ПОСТАВЩИКОВ

class Complaint(Base):
    # ТАБЛИЦА ПРЕТЕНЗИЙ ОТ КЛИЕНТОВ
    __tablename__ = 'complaints'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders_clients.id')) # ЗАКАЗ КЛИЕНТА
    ticket_id = Column(Integer, ForeignKey('tickets.id')) # БИЛЕТ КЛИЕНТА
    description = Column(Text, nullable=False) # ОПИСАНИЕ ПРЕТЕНЗИЙ
    date = Column(DateTime, nullable=False) # ДАТА СОСТАВЛЕНИЯ ПРЕТЕНЗИЙ
    status = Column(Text, default="на рассмотрении") # СТАТУС ПРЕТЕНЗИЙ: "решён", "не решён", "на рассмотрений"
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    order = relationship("OrderClients", back_populates="complaint") # СВЯЗЬ С ТАБЛИЦЕЙ ПОКУПОК КЛИЕНТА
    ticket = relationship("Ticket", back_populates="complaint") # СВЯЗЬ С ТАБЛИЦЕЙ БИЛЕТОВ
