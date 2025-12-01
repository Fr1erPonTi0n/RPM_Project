# ORM МОДЕЛЬ ДЛЯ: 
# - УПРАВЛЕНИЯМИ РЕЕСТРОМ ПОСТАВЩИКОВ

from database import Base
from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

# ТАБЛИЦА ДЛЯ СВЯЗИ МНОГИЕ-КО-МНОГИМ: ПОСТАВЩИКИ - ТИПЫ ПОСТАВОК
supplier_supply_type = Table(
    'supplier_supply_type',
    Base.metadata,
    Column('supplier_id', Integer, ForeignKey('suppliers.id')),
    Column('supply_type_id', Integer, ForeignKey('supply_types.id'))
)

class Supplier(Base):
    # ТАБЛИЦА ПОСТАВЩИКОВ
    __tablename__ = 'suppliers'

    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # ИМЯ ПОСТАВЩИКА
    contact_info = Column(Text) # КОНТАКТНАЯ ИНФОРМАЦИЯ ПОСТАВЩИКА
    details = Column(Text) # РЕКВИЗИТЫ ПОСТАВЩИКА
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    contracts = relationship("Contract", back_populates="supplier") # СВЯЗЬ С ТАБЛИЦЕЙ КОНТРАКТОВ
    licenses = relationship("License", back_populates="supplier") # СВЯЗЬ С ТАБЛИЦЕЙ ЛИЦЕНЗИЙ
    orders = relationship("OrderSupliers", back_populates="supplier") # СВЯЗЬ С ТАБЛИЦЕЙ ЗАКАЗОВ
    kpi = relationship("SupplierKPI", back_populates="supplier", uselist=False) # СВЯЗЬ СО СРАВНИТЕЛЬНОЙ ТАБЛИЦЕЙ ПОСТАВЩИКОВ
    supply_types = relationship("SupplyType", secondary=supplier_supply_type, back_populates="supplier") # СВЯЗЬ С ТАБЛИЦЕЙ ТИПОВ ПОСТАВЩИКОВ

class SupplyType(Base):
    # ТАБЛИЦА ТИПОВ ПОСТАВЩИКОВ
    __tablename__ = 'supply_types'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)  # ТИПЫ ПОСТАВЩИКОВ: "кино", "товары", "услуги"
    description = Column(Text) # ОПИСАНИЕ ТИПА ПОСТАВЛЯЕМЫХ ТОВАРОВ ИЛИ УСЛУГ
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    supplier = relationship("Supplier", secondary=supplier_supply_type, back_populates="supply_types") # СВЯЗЬ С ТАБЛИЦЕЙ ПОСТАВЩИКОВ
