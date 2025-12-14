# КОНФИГУРАЦИОННЫЙ ФАЙЛ

import os
import sys

def get_database_path():
    """Определяет путь к базе данных для разных режимов запуска"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable) # Если запущено как EXE
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__)) # Если запущено как скрипт Python
    return os.path.join(base_dir, "database.db")

DATABASE_URL = f"sqlite:///{get_database_path()}"
