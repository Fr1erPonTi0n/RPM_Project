# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ АДМИНИСТРАТОРА КОНТЕНТА
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QTableWidget)
from PyQt6.QtCore import Qt
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ContentMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Администратор")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Администратор")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.film_button = QPushButton("Работа с фильмами")
        self.screening_button = QPushButton("Работа с показами")
        self.ticket_button = QPushButton("Работа с билетами")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.film_button.setStyleSheet(button_style)
        self.screening_button.setStyleSheet(button_style)
        self.ticket_button.setStyleSheet(button_style)
        
        layout.addWidget(self.film_button)
        layout.addWidget(self.screening_button)
        layout.addWidget(self.ticket_button)

        self.film_button.clicked.connect(self.open_film_window)
        self.screening_button.clicked.connect(self.open_screening_window)
        self.ticket_button.clicked.connect(self.open_ticket_window)

    def open_film_window(self):
        self.film_window = FilmWindow()
        self.film_window.show()

    def open_screening_window(self):
        self.screening_window = ScreeningWindow()
        self.screening_window.show()

    def open_ticket_window(self):
        self.ticket_window = TicketWindow()
        self.ticket_window.show()
    

class FilmWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Меню работы с фильмами")
        self.setGeometry(100, 100, 500, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Меню работы с фильмами")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Длительность"])
        layout.addWidget(self.tableWidget)

        self.add_button = QPushButton("Добавить фильм")
        self.update_button = QPushButton("Редактировать информацию о фильме")
        self.delete_button = QPushButton("Удалить фильм")

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


class ScreeningWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Меню работы с показами")
        self.setGeometry(100, 100, 500, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Меню работы с показами")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Фильм", "Дата", "Зал"])
        layout.addWidget(self.tableWidget)

        self.add_button = QPushButton("Создать показ")
        self.update_button = QPushButton("Редактировать информацию о показе")
        self.delete_button = QPushButton("Удалить показ")

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


class TicketWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Меню работы с билетами")
        self.setGeometry(100, 100, 500, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Меню работы с билетами")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Показ", "Место", "Статус"])
        layout.addWidget(self.tableWidget)

        self.add_button = QPushButton("Создать билет")
        self.update_button = QPushButton("Редактировать информацию о билете")
        self.delete_button = QPushButton("Удалить / отменить билет")

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