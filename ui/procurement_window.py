# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ МЕНЕДЖЕРА ПО ЗАКУПКАМ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QPushButton, QTableWidget, 
                             QTableWidgetItem)
from PyQt6.QtCore import Qt
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ProcurementMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Управление закупками")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Управление закупками")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.supplier_button = QPushButton("Работа с поставщиками")
        self.license_button = QPushButton("Работа с лицензиями")
        self.order_button = QPushButton("Работа с заказами")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.supplier_button.setStyleSheet(button_style)
        self.license_button.setStyleSheet(button_style)
        self.order_button.setStyleSheet(button_style)
        
        layout.addWidget(self.supplier_button)
        layout.addWidget(self.license_button)
        layout.addWidget(self.order_button)

        self.supplier_button.clicked.connect(self.open_supplier_window)
        self.license_button.clicked.connect(self.open_license_window)
        self.order_button.clicked.connect(self.open_order_window)

    def open_supplier_window(self):
        self.supplier_window = SuplierWindow()
        self.supplier_window.show()

    def open_license_window(self):
        self.license_window = LicenseWindow()
        self.license_window.show()

    def open_order_window(self):
        self.order_window = OrderWindow()
        self.order_window.show()
    
class SuplierWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Работа с поставщиками")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Работа с поставщиками")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Контакты"])
        layout.addWidget(self.tableWidget)

        self.add_button = QPushButton("Добавить")
        self.update_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.add_button.setStyleSheet(button_style)
        self.update_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        
        layout.addWidget(self.add_button)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)

        self.add_button.clicked.connect(self.funcx)
        self.update_button.clicked.connect(self.funcx)
        self.delete_button.clicked.connect(self.funcx)

    def funcx(self):
        pass

class LicenseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Работа с лицензиями")
        self.setGeometry(100, 100, 500, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Работа с лицензиями")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Тип", "Срок", "Статус", "Поставщик"])
        layout.addWidget(self.tableWidget)

        self.add_button = QPushButton("Добавить лицензию")
        self.update_button = QPushButton("Редактировать информацию о лицензии")
        self.delete_button = QPushButton("Удалить лицензию / расторгнуть")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.add_button.setStyleSheet(button_style)
        self.update_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        
        layout.addWidget(self.add_button)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)

        self.add_button.clicked.connect(self.funcx)
        self.update_button.clicked.connect(self.funcx)
        self.delete_button.clicked.connect(self.funcx)

    def funcx(self):
        pass

class OrderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Работа с заказами")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Работа с заказами")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Поставщик", "Лицензия", "Статус/Описание заказа"])
        layout.addWidget(self.tableWidget)

        self.add_button = QPushButton("Создать заказ")
        self.update_button = QPushButton("Редактировать информацию о заказе")
        self.delete_button = QPushButton("Отменимть заказ")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.add_button.setStyleSheet(button_style)
        self.update_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        
        layout.addWidget(self.add_button)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)

        self.add_button.clicked.connect(self.funcx)
        self.update_button.clicked.connect(self.funcx)
        self.delete_button.clicked.connect(self.funcx)

    def funcx(self):
        pass
