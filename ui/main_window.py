# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ ОСНОВНОГО МЕНЮ ДЛЯ УПРАВЛЕНИЯ ДРУГИМИ ОКНАМИ
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel)
from PyQt6.QtCore import Qt
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.content_window import ContentWindow
from ui.finance_window import FinanceWindow
from ui.procurement_window import ProcurementWindow
from ui.notification_dialog import NotificationDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("SRM-Система кинотеатр")
        self.setGeometry(100, 100, 400, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        self.title_label = QLabel("SRM-Система кинотеатр")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.content_button = QPushButton("Работа с контентом")
        self.finance_button = QPushButton("Работа с аналитикой")
        self.procurement_button = QPushButton("Работа с закупками / лицензиями")
        self.notification_button = QPushButton("Увемедомления")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.content_button.setStyleSheet(button_style)
        self.finance_button.setStyleSheet(button_style)
        self.procurement_button.setStyleSheet(button_style)
        self.notification_button.setStyleSheet(button_style)
        
        layout.addWidget(self.content_button)
        layout.addWidget(self.finance_button)
        layout.addWidget(self.procurement_button)
        layout.addWidget(self.notification_button)
        
        central_widget.setLayout(layout)

        self.content_button.clicked.connect(self.open_content_window)
        self.finance_button.clicked.connect(self.open_finance_window)
        self.procurement_button.clicked.connect(self.open_procurement_window)
        self.notification_button.clicked.connect(self.open_notification_dialog)
    
    def open_content_window(self):
        """Открытие окна просмотра студентов"""
        self.content_window = ContentWindow()
        self.content_window.show()
    
    def open_finance_window(self):
        """Открытие окна добавления студента"""
        self.finance_window = FinanceWindow()
        self.finance_window.show()

    def open_procurement_window(self):
        self.procurement_window = ProcurementWindow()
        self.procurement_window.show()

    def open_notification_dialog(self):
        self.notification_dialog = NotificationDialog()
        self.notification_dialog.show()