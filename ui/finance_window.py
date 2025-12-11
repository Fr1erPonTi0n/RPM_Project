# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ МЕНЕДЖЕРА ПО ЗАКУПКАМ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QPushButton, QTableWidget, 
                             QTableWidgetItem)
from PyQt6.QtCore import Qt
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FinanceMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Финансовая аналитика")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Финансовая аналитика")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.revenue_button = QPushButton("Посмотреть выручку")
        self.attendance_button = QPushButton("Посмотреть посещаемость")
        self.popular_movie_button = QPushButton("Посмотреть популярные фильмы")

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """
        self.revenue_button.setStyleSheet(button_style)
        self.attendance_button.setStyleSheet(button_style)
        self.popular_movie_button.setStyleSheet(button_style)
        
        layout.addWidget(self.revenue_button)
        layout.addWidget(self.attendance_button)
        layout.addWidget(self.popular_movie_button)

        self.revenue_button.clicked.connect(self.open_revenue_window)
        self.attendance_button.clicked.connect(self.open_attendance_window)
        self.popular_movie_button.clicked.connect(self.open_popular_movie_window)

    def open_revenue_window(self):
        self.revenue_window = RevenueWindow()
        self.revenue_window.show()

    def open_attendance_window(self):
        self.attendance_window = AttendanceWindow()
        self.attendance_window.show()

    def open_popular_movie_window(self):
        self.popular_movie_window = PopularMovieWindow()
        self.popular_movie_window.show()
    

class RevenueWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Выручка")
        self.setGeometry(100, 100, 500, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Выручка")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Дата", "Билеты", "Сумма", "Среднняя цена"])
        layout.addWidget(self.tableWidget)

    def funcx(self):
        pass


class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Посещаемость")
        self.setGeometry(100, 100, 750, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Посещаемость")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(["ID показа", "Фильм", "Зал", "Мест всего", "Продано", "Свободно", "% заполняемости"])
        layout.addWidget(self.tableWidget)

    def funcx(self):
        pass


class PopularMovieWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Популярные фильмы")
        self.setGeometry(100, 100, 500, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Популярные фильмы")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Рейтинг", "Название", "Билеты", "Выручка", "Средняя цена"])
        layout.addWidget(self.tableWidget)

    def func(self):
        pass
