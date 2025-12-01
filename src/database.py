# ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ БД, ORM-МОДЕЛИ SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок (engine) для подключения к базе даннных, но не экспортируем его
_engine = create_engine(DATABASE_URL, echo=True)

# Фабрика для создания сессий
SessionLocal = sessionmaker(bind=_engine)

# Функция для инициализация базы данных
def init_db():
    Base.metadata.create_all(bind=_engine)
