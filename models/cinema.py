# ORM МОДЕЛЬ ДЛЯ: 
# - УПРАВЛЕНИЕ КИНОТЕАТРОМ

from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base

class Film(Base):
    # ТАБЛИЦА ФИЛЬМОВ
    __tablename__ = 'films'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey('licenses.id')) # ЛИЦЕНЗИЯ К КОТОРОМУ ПРИВЯЗАН ФИЛЬМ
    title = Column(Text, nullable=False) # НАЗВАНИЕ ФИЛЬМА
    duration = Column(Integer) # ДЛИТЕЛЬНОСТЬ ФИЛЬМА В МИНУТАХ С ОКРУГЛЕНИЕМ
    description = Column(Text) # ОПИСАНИЕ ФИЛЬМА 
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    license = relationship("License", back_populates="film") # СВЯЗЬ С ТАБЛИЦЕЙ ЛИЦЕНЗИЙ
    screenings = relationship("Screening", back_populates="film") # СВЯЗЬ С ТАБЛИЦЕЙ ПОКАЗОВ

class Screening(Base):
    # ТАБЛИЦА ПОКАЗОВ ФИЛЬМОВ
    __tablename__ = 'screenings'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    film_id = Column(Integer, ForeignKey('films.id')) # ФИЛЬМ, КОТОРЫЙ ПРИВЯЗАН К ПОКАЗУ
    datetime = Column(DateTime, nullable=False) # ДАТА И ВРЕМЯ НАЧАЛА ФИЛЬМА
    hall = Column(Text, nullable=False) # ЗАЛ, В КОТОРОМ БУДЕТ ПРОВОДИТЬСЯ ФИЛЬМ
    ticket_price = Column(Float, nullable=False) # ЦЕНА БИЛЕТА НА ФИЛЬМ
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    film = relationship("Film", back_populates="screenings") # СВЯЗЬ С ТАБЛИЦЕЙ ФИЛЬМОВ
    ticket = relationship("Ticket", back_populates="screening") # СВЯЗЬ С ТАБЛИЦЕЙ БИЛЕТОВ

class Ticket(Base):
    # ТАБЛИЦА БИЛЕТОВ
    __tablename__ = 'tickets'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    screening_id = Column(Integer, ForeignKey('screenings.id')) # СВЯЗЬ С ПОКАЗОМ
    order_id = Column(Integer, ForeignKey('orders_clients.id')) # СВЯЗЬ С ЗАКАЗОМ КЛИЕНТА
    seat_number = Column(Text, nullable=False) # НОМЕР МЕСТА ДЛЯ ЗРИТЕЛЯ
    price = Column(Float, nullable=False) # ЦЕНА БИЛЕТА
    sold = Column(Boolean, default=False) # СТАТУС БИЛЕТА (ПРОДАН, НЕ ПРОДАН)
    sold_date = Column(DateTime) # ДАТА ПРОДАЖИ БИЛЕТА
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    screening = relationship("Screening", back_populates="ticket") # СВЯЗЬ С ТАБЛИЦЕЙ ПОКАЗОВ
    complaint = relationship("Complaint", back_populates="ticket") # СВЯЗЬ С ТАБЛИЦЕЙ ЖАЛОБ
    order = relationship("OrderClients", back_populates='ticket') # СВЯЗЬ С ПОКУПКАМИ
    
