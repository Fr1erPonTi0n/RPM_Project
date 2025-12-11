# ORM МОДЕЛЬ ДЛЯ: 
# - УПРАВЛЕНИЯМИ КОНТРАКТАМИ И ЛИЦЕНЗИЯМИ

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base

class Contract(Base):
    # ТАБЛИЦЫ КОНТРАКТОВ С ПОСТАВЩИКАМИ
    __tablename__ = 'contracts'

    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id')) # ПОСТАВЩИК, С КОТОРЫМ БЫЛ ЗАКЛЮЧЁН КОНТРАКТ
    title = Column(String(200), nullable=False) # НАЗВАНИЕ КОНТРАКТА
    start_date = Column(Date, nullable=False) # ДАТА ОФОРМЛЕНИЯ КОНТРАКТА
    end_date = Column(Date, nullable=False) # ДАТА ОКОНЧАНИЯ КОНТРАКТА
    file_path = Column(String(300)) # ПУТЬ К ФАЙЛУ КОНТРАКТА
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    supplier = relationship("Supplier", back_populates="contracts") # СВЯЗЬ С ТАБЛИЦЕЙ ПОСТАВЩИКОВ
    license = relationship("License", back_populates="contract") # СВЯЗЬ С ТАБЛИЦЕЙ ЛИЦЕНЗИЙ
    order = relationship("OrderSupliers", back_populates="contract") # СВЯЗЬ С ТАБЛИЦЕЙ ЗАКАЗОВ ПОСТАВЩИКОВ

class License(Base):
    # ТАБЛИЦЫ ЛИЦЕНЗИЙ НА ФИЛЬМЫ
    __tablename__ = 'licenses'

    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id')) # ПОСТАВЩИК, КОТОРЫЙ ПРЕДОСТАВЛЯЕТ ЛИЦЕНЗИЮ
    contract_id = Column(Integer, ForeignKey('contracts.id')) # КОНТРАКТ, КОТОРЫЙ БЫЛ ЗАКЛЮЧЁН С ПОСТАВЩИКОМ
    film_title = Column(String(200), nullable=False) # НАЗВАНИЕ ФИЛЬМА
    digital_key = Column(String(100)) # ЦИФРОВОЙ КЛЮЧ ДЛЯ ФИЛЬМА
    start_date = Column(Date, nullable=False) # ДАТА ОФОРМЛЕНИЯ ЛИЦЕНЗИЙ
    end_date = Column(Date, nullable=False) # ДАТА ОКОНЧАНИЯ ЛИЦЕНЗИЙ
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    supplier = relationship("Supplier", back_populates="licenses") # СВЯЗЬ С ТАБЛИЦЕЙ ПОСТАВЩИКОВ
    contract = relationship("Contract", back_populates="license") # СВЯЗЬ С ТАБЛИЦЕЙ КОНТРАКТОВ
    film = relationship("Film", back_populates="license", uselist=False) # СВЯЗЬ С ТАБЛИЦЕЙ ФИЛЬМОВ
    
