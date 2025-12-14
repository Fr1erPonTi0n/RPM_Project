from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок (engine) для подключения к базе даннных
_engine = create_engine(DATABASE_URL, echo=True)

# Фабрика для создания сессий
SessionLocal = sessionmaker(bind=_engine)

# Функция для инициализация базы данных
def init_db():
    from models.supplier import Supplier, SupplyType, supplier_supply_type
    from models.license import Contract, License
    from models.cinema import Film, Screening, Ticket
    from models.procurement import OrderSupliers, OrderClients, OrderItem
    from models.analytics import SupplierKPI, Complaint
    
    # Создаём таблицы в правильном порядке
    tables = [
        Supplier.__table__,
        SupplyType.__table__,
        supplier_supply_type,
        Contract.__table__,
        License.__table__,
        Film.__table__,
        Screening.__table__,
        OrderClients.__table__,
        Ticket.__table__,
        OrderSupliers.__table__,
        OrderItem.__table__,
        SupplierKPI.__table__,
        Complaint.__table__
    ]
    
    Base.metadata.create_all(bind=_engine, tables=tables)
