# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ МЕНЕДЖЕРА ПО ЗАКУПКАМ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHBoxLayout,
                             QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.cinema_service import get_daily_revenue, get_popular_films, get_screening_attendance
from services.cinema_service import get_screenings_for_date

class FinanceMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Финансовая аналитика")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.title_label = QLabel("Финансовая аналитика")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)

        # Панель управления
        control_panel = QHBoxLayout()

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        btn_revenue = QPushButton("Выручка за день")
        btn_popular = QPushButton("Популярные фильмы")
        btn_attendance = QPushButton("Посещаемость")

        control_panel.addWidget(QLabel("Дата:"))
        control_panel.addWidget(self.date_input)
        control_panel.addWidget(btn_revenue)
        control_panel.addWidget(btn_popular)
        control_panel.addWidget(btn_attendance)

        layout.addLayout(control_panel)

        # Таблица для результатов
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)

        # Подключаем обработчики
        btn_revenue.clicked.connect(self.show_revenue)
        btn_popular.clicked.connect(self.show_popular)
        btn_attendance.clicked.connect(self.show_attendance)

    def clear_table(self):
        """Очистить таблицу"""
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

    def show_revenue(self):
        """Показать выручку за выбранный день"""
        db = SessionLocal()  # Создаем локальную сессию
        try:
            date_str = self.date_input.date().toString("yyyy-MM-dd")
            revenue_data = get_daily_revenue(db, date_str)  # Используем локальную сессию

            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(["Показатель", "Значение", "Описание"])
            self.tableWidget.setRowCount(5)

            data = [
                ("Дата", str(revenue_data['date']), "Анализируемый день"),  # Просто преобразуем в строку
                ("Продано билетов", str(revenue_data['total_tickets_sold']), "Всего проданных билетов"),
                ("Общая выручка", f"{revenue_data['total_revenue']:.2f} руб.", "Суммарная выручка"),
                ("Средняя цена", f"{revenue_data['average_ticket_price']:.2f} руб.", "Средняя цена билета"),
                ("Фильмы", str(len(revenue_data['revenue_by_film'])), "Количество фильмов")
            ]

            for row, (name, value, desc) in enumerate(data):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(name))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(value)))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(desc))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()  # Закрываем сессию

    def show_popular(self):
        """Показать популярные фильмы"""
        try:
            popular_films = get_popular_films(self.db, limit=5, days=30)

            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["Рейтинг", "Фильм", "Билеты", "Выручка", "Ср. цена"])
            self.tableWidget.setRowCount(len(popular_films))

            for row, film in enumerate(popular_films):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(film['rank'])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(film['film_title']))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(film['tickets_sold'])))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(f"{film['total_revenue']:.2f} руб."))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(f"{film['average_ticket_price']:.2f} руб."))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_attendance(self):
        """Показать посещаемость за выбранный день"""
        try:
            date_str = self.date_input.date().toString("yyyy-MM-dd")
            screenings = self.get_screenings_for_date(date_str)

            self.tableWidget.setColumnCount(7)
            self.tableWidget.setHorizontalHeaderLabels([
                "ID", "Фильм", "Зал", "Всего мест", "Продано", "Свободно", "% заполняемости"
            ])
            self.tableWidget.setRowCount(len(screenings))

            for row, screening in enumerate(screenings):
                attendance = get_screening_attendance(self.db, screening['id'])

                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(screening['id'])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(attendance['film_title']))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(attendance['hall']))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(str(attendance['total_seats'])))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(str(attendance['seats_sold'])))
                self.tableWidget.setItem(row, 5, QTableWidgetItem(str(attendance['seats_available'])))
                self.tableWidget.setItem(row, 6, QTableWidgetItem(f"{attendance['occupancy_rate']:.1f}%"))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_attendance(self):
        """Показать посещаемость за выбранный день"""
        db = SessionLocal()  # Создаем локальную сессию
        try:
            date_str = self.date_input.date().toString("yyyy-MM-dd")
            # Используем новую функцию
            screenings = get_screenings_for_date(db, date_str)

            if not screenings:
                QMessageBox.information(self, "Информация", "На выбранную дату показов нет")
                self.clear_table()
                return

            self.tableWidget.setColumnCount(7)
            self.tableWidget.setHorizontalHeaderLabels([
                "ID", "Фильм", "Время", "Зал", "Цена", "Продано", "Выручка"
            ])
            self.tableWidget.setRowCount(len(screenings))

            for row, screening in enumerate(screenings):
                attendance = get_screening_attendance(db, screening['id'])

                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(screening['id'])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(screening['film_title']))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(screening['datetime'].strftime("%H:%M")))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(screening['hall']))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(f"{screening['ticket_price']:.2f} руб."))
                self.tableWidget.setItem(row, 5, QTableWidgetItem(str(attendance['seats_sold'])))
                self.tableWidget.setItem(row, 6, QTableWidgetItem(f"{attendance['total_revenue']:.2f} руб."))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()
