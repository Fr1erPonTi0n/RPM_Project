# ORM МОДЕЛЬ ДЛЯ: 
# - УПРАВЛЕНИЯМИ ЗАКУПОЧНОЙ ДЕЯТЕЛЬНОСТИ ПОСТАВЩИКОВ
# - УПРАВЛЕНИЯМИ ПОКУПКАМИ КЛИЕНТОВ

from database import Base
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

class OrderSupliers(Base):
    # ТАБЛИЦА ЗАКАЗОВ ПОСТАВЩИКОВ
    __tablename__ = 'orders_supliers'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id')) # ПОСТАВЩИК, С КОТОРЫМ СВЯЗАН ЗАКАЗ
    contract_id = Column(Integer, ForeignKey('contracts.id')) # КОНТРАКТ, НА ОСНОВЕ КОТОРОГО БЫЛ ЗАКЛЮЧЁН ЗАКАЗ
    status = Column(String(50), default="создан") # СТАТУС ЗАКАЗА: "создан", "в процессе", "доставлен", "отменен"
    created_date = Column(DateTime, nullable=False) # ДАТА СОЗДАНИЯ ЗАКАЗА
    delivery_date = Column(Date) # ДАТА ДОСТАВКИ ЗАКАЗА
    total_amount = Column(Float, default=0.0) # ОБЩАЯ СУММА
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    supplier = relationship("Supplier", back_populates="orders") # СВЯЗЬ С ТАБЛИЦЕЙ ПОСТАВЩИКОВ
    contract = relationship("Contract", back_populates="order") # СВЯЗЬ С ТАБЛИЦЕЙ КОНТРАКТОВ
    items = relationship("OrderItem", back_populates="order") # СВЯЗЬ С ТАБЛИЦЕЙ ЗАКАЗНЫХ ТОВАРОВ

class OrderClients(Base):
    # ТАБЛИЦА ПОКУПОК КЛИЕНТОВ
    __tablename__ = 'orders_clients'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(200)) # ИМЯ КЛИЕНТА
    phone = Column(String(50)) # ТЕЛЕФОН КЛИЕНТА
    order_date = Column(DateTime, nullable=False) # ДАТА ЗАКАЗА
    total_amount = Column(Float, default=0.0) # ОБЩАЯ СУММА
    status = Column(String(50), default="оформлен") # СТАТУС ЗАКАЗА
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    complaint = relationship("Complaint", back_populates="order") # СВЯЗЬ С ТАБЛИЦЕЙ ПРЕТЕНЗИЙ ОТ КЛИЕНТОВ
    ticket = relationship("Ticket", back_populates="order") # СВЯЗЬ С ТАБЛИЦЕЙ БИЛЕТОВ

class OrderItem(Base):
    # ТАБЛИЦА ЗАКАЗНЫХ ТОВАРОВ
    __tablename__ = 'order_items'
    
    # ОСНОВНЫЕ СТОЛБЦЫ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders_supliers.id')) # ЗАКАЗ, С КОТОРЫМ СВЯЗАН ТОВАР
    product_name = Column(String(200), nullable=False) # НАЗВАНИЕ ТОВАРА
    quantity = Column(Integer, nullable=False) # КОЛИЧЕСТВО ТОВАРА
    price = Column(Float, nullable=False) # ЦЕНА ЗА ЕДИНИЦУ
    total_price = Column(Float, nullable=False) # ОБЩАЯ ЦЕНА
    
    # СВЯЗИ ДЛЯ СОЗДАНИЕ ТАБЛИЦЫ
    order = relationship("OrderSupliers", back_populates="items") # СВЯЗЬ С ТАБЛИЦЕЙ ЗАКАЗОВ ПОСТАВЩИКОВ
    
