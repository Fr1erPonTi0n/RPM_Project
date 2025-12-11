# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ МЕНЕДЖЕРА ПО ЗАКУПКАМ
from PyQt6.QtWidgets import (QWidget)
from PyQt6.QtCore import Qt
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProcurementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        pass