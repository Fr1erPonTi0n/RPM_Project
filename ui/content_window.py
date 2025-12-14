# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ АДМИНИСТРАТОРА КОНТЕНТА
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHBoxLayout,
                             QLineEdit, QMessageBox, QDialog, QFormLayout,
                             QSpinBox, QTextEdit, QDateTimeEdit)
from PyQt6.QtCore import Qt, QDateTime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.cinema_service import (create_film, get_all_films, get_film_by_id,
                                     delete_film, create_screening, get_all_screenings,
                                     update_screening, delete_screening)


class ContentMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Управление контентом")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.title_label = QLabel("Управление контентом")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)

        # Кнопки переключения
        button_panel = QHBoxLayout()
        btn_films = QPushButton("Фильмы")
        btn_screenings = QPushButton("Показы")

        button_panel.addWidget(btn_films)
        button_panel.addWidget(btn_screenings)
        layout.addLayout(button_panel)

        # Панель управления
        self.control_panel = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        self.refresh_btn = QPushButton("Обновить")

        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]:
            btn.setStyleSheet("font-size: 12px; padding: 5px; margin: 2px;")
            self.control_panel.addWidget(btn)

        layout.addLayout(self.control_panel)

        # Таблица
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)

        # Начальная загрузка фильмов
        self.current_mode = "films"
        self.load_films()

        # Обработчики
        btn_films.clicked.connect(lambda: self.switch_mode("films"))
        btn_screenings.clicked.connect(lambda: self.switch_mode("screenings"))
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.refresh_btn.clicked.connect(self.refresh_data)

    def switch_mode(self, mode):
        """Переключение между режимами"""
        self.current_mode = mode
        self.refresh_data()

    def refresh_data(self):
        """Обновить данные в зависимости от режима"""
        if self.current_mode == "films":
            self.load_films()
        else:
            self.load_screenings()

    def load_films(self):
        """Загрузить список фильмов"""
        try:
            films = get_all_films(self.db)
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Длительность", "Описание"])
            self.tableWidget.setRowCount(len(films))

            for row, film in enumerate(films):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(film.id)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(film.title))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(f"{film.duration} мин"))
                desc = film.description[:50] + "..." if len(film.description) > 50 else film.description
                self.tableWidget.setItem(row, 3, QTableWidgetItem(desc))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def load_screenings(self):
        """Загрузить список показов"""
        try:
            screenings = get_all_screenings(self.db)
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Фильм", "Дата", "Зал", "Цена"])
            self.tableWidget.setRowCount(len(screenings))

            for row, screening in enumerate(screenings):
                film = get_film_by_id(self.db, screening.film_id)
                film_name = film.title if film else f"ID:{screening.film_id}"

                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(screening.id)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(film_name))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(screening.datetime.strftime("%d.%m.%Y %H:%M")))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(screening.hall))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(f"{screening.ticket_price:.2f} руб."))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def get_selected_id(self):
        """Получить ID выбранной строки"""
        row = self.tableWidget.currentRow()
        if row >= 0:
            return int(self.tableWidget.item(row, 0).text())
        return None

    def add_item(self):
        """Добавить новый элемент"""
        if self.current_mode == "films":
            dialog = FilmDialog(self.db)  # Передаем сессию
        else:
            dialog = ScreeningDialog(self.db)  # Передаем сессию

        if dialog.exec():
            self.refresh_data()

    def edit_item(self):
        """Редактировать выбранный элемент"""
        item_id = self.get_selected_id()
        if not item_id:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент для редактирования")
            return

        if self.current_mode == "films":
            dialog = FilmDialog(self.db, item_id)  # Передаем сессию
        else:
            dialog = ScreeningDialog(self.db, item_id)  # Передаем сессию

        if dialog.exec():
            self.refresh_data()

    def delete_item(self):
        """Удалить выбранный элемент"""
        item_id = self.get_selected_id()
        if not item_id:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент для удаления")
            return

        name = self.tableWidget.item(self.tableWidget.currentRow(), 1).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.current_mode == "films":
                    success = delete_film(self.db, item_id)
                else:
                    success = delete_screening(self.db, item_id)

                if success:
                    QMessageBox.information(self, "Успех", "Элемент удален")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))


class FilmDialog(QDialog):
    def __init__(self, db, film_id=None):
        super().__init__()
        self.db = db
        self.film_id = film_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Фильм" if not self.film_id else "Редактировать фильм")
        self.setGeometry(200, 200, 400, 250)

        layout = QFormLayout()

        self.title_input = QLineEdit()
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 300)
        self.duration_input.setValue(120)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)

        layout.addRow("Название:", self.title_input)
        layout.addRow("Длительность (мин):", self.duration_input)
        layout.addRow("Описание:", self.description_input)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)

        self.setLayout(layout)

        # Если редактируем, загружаем данные
        if self.film_id:
            self.load_data()

    def load_data(self):
        try:
            film = get_film_by_id(self.db, self.film_id)
            if film:
                self.title_input.setText(film.title)
                self.duration_input.setValue(film.duration)
                self.description_input.setText(film.description)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def save(self):
        try:
            if self.film_id:
                # Редактирование существующего фильма
                film = get_film_by_id(self.db, self.film_id)
                if film:
                    film.title = self.title_input.text()
                    film.duration = self.duration_input.value()
                    film.description = self.description_input.toPlainText()

                    self.db.add(film)
                    self.db.commit()

                    QMessageBox.information(self, "Успех", "Фильм обновлен")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Фильм не найден")
            else:
                # Создание нового фильма
                film = create_film(
                    self.db,  # Используем self.db
                    license_id=1,  # TODO: Добавить выбор лицензии
                    title=self.title_input.text(),
                    duration=self.duration_input.value(),
                    description=self.description_input.toPlainText()
                )
                QMessageBox.information(self, "Успех", f"Фильм создан (ID: {film.id})")
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class ScreeningDialog(QDialog):
    def __init__(self, db, screening_id=None):
        super().__init__()
        self.db = db  # Сохраняем сессию
        self.screening_id = screening_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Показ" if not self.screening_id else "Редактировать показ")
        self.setGeometry(200, 200, 400, 300)

        layout = QFormLayout()

        self.film_id_input = QSpinBox()
        self.film_id_input.setRange(1, 1000)

        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(QDateTime.currentDateTime().addDays(1))

        self.hall_input = QLineEdit()
        self.hall_input.setText("Зал 1")

        self.price_input = QLineEdit()
        self.price_input.setText("300")

        layout.addRow("ID фильма:", self.film_id_input)
        layout.addRow("Дата и время:", self.datetime_input)
        layout.addRow("Зал:", self.hall_input)
        layout.addRow("Цена:", self.price_input)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)

        self.setLayout(layout)

    def save(self):
        try:
            if self.screening_id:
                # Обновляем показ
                result = update_screening(
                    self.db,  # Используем self.db
                    self.screening_id,
                    datetime_str=self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm"),
                    hall=self.hall_input.text(),
                    ticket_price=float(self.price_input.text())
                )
                if result:
                    QMessageBox.information(self, "Успех", "Показ обновлен")
                    self.accept()
            else:
                # Создаем новый показ
                screening = create_screening(
                    self.db,  # Используем self.db
                    film_id=self.film_id_input.value(),
                    datetime_str=self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm"),
                    hall=self.hall_input.text(),
                    ticket_price=float(self.price_input.text())
                )
                QMessageBox.information(self, "Успех", f"Показ создан (ID: {screening.id})")
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))