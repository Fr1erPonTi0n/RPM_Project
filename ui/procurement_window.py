# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА ДЛЯ МЕНЕДЖЕРА ПО ЗАКУПКАМ
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHBoxLayout,
                             QMessageBox, QDialog, QFormLayout, QLineEdit,
                             QSpinBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.supplier_service import create_supplier, get_all_suppliers, delete_supplier
from services.license_service import create_contract, get_all_contracts, create_license, get_all_licenses
from services.license_service import delete_contract, delete_license

class ProcurementMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Управление закупками")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.title_label = QLabel("Управление закупками")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)

        # Кнопки переключения
        button_panel = QHBoxLayout()
        self.btn_suppliers = QPushButton("Поставщики")
        self.btn_contracts = QPushButton("Контракты")
        self.btn_licenses = QPushButton("Лицензии")

        for btn in [self.btn_suppliers, self.btn_contracts, self.btn_licenses]:
            btn.setStyleSheet("font-size: 14px; padding: 8px; margin: 3px;")
            button_panel.addWidget(btn)

        layout.addLayout(button_panel)

        # Панель управления
        self.control_panel = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.delete_btn = QPushButton("Удалить")
        self.refresh_btn = QPushButton("Обновить")

        for btn in [self.add_btn, self.delete_btn, self.refresh_btn]:
            btn.setStyleSheet("font-size: 12px; padding: 5px; margin: 2px;")
            self.control_panel.addWidget(btn)

        layout.addLayout(self.control_panel)

        # Таблица
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)

        # Начальная загрузка
        self.current_mode = "suppliers"
        self.load_suppliers()

        # Обработчики
        self.btn_suppliers.clicked.connect(lambda: self.switch_mode("suppliers"))
        self.btn_contracts.clicked.connect(lambda: self.switch_mode("contracts"))
        self.btn_licenses.clicked.connect(lambda: self.switch_mode("licenses"))
        self.add_btn.clicked.connect(self.add_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.refresh_btn.clicked.connect(self.refresh_data)

    def switch_mode(self, mode):
        """Переключение между режимами"""
        self.current_mode = mode
        self.refresh_data()

    def refresh_data(self):
        """Обновить данные"""
        if self.current_mode == "suppliers":
            self.load_suppliers()
        elif self.current_mode == "contracts":
            self.load_contracts()
        else:
            self.load_licenses()

    def load_suppliers(self):
        """Загрузить поставщиков"""
        db = SessionLocal()
        try:
            suppliers = get_all_suppliers(db)
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Контакты"])
            self.tableWidget.setRowCount(len(suppliers))

            for row, supplier in enumerate(suppliers):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(supplier.id)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(supplier.name))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(supplier.contact_info or ""))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()

    def load_contracts(self):
        """Загрузить контракты"""
        db = SessionLocal()
        try:
            contracts = get_all_contracts(db)
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Поставщик", "Начало", "Окончание"])
            self.tableWidget.setRowCount(len(contracts))

            for row, contract in enumerate(contracts):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(contract.id)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(contract.title))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(contract.supplier_id)))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(contract.start_date.strftime("%d.%m.%Y")))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(contract.end_date.strftime("%d.%m.%Y")))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()

    def load_licenses(self):
        """Загрузить лицензии"""
        db = SessionLocal()
        try:
            licenses = get_all_licenses(db)
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Фильм", "Поставщик", "Контракт", "Срок"])
            self.tableWidget.setRowCount(len(licenses))

            for row, license_obj in enumerate(licenses):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(license_obj.id)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(license_obj.film_title))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(license_obj.supplier_id)))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(str(license_obj.contract_id)))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(
                    f"{license_obj.start_date.strftime('%d.%m.%Y')} - {license_obj.end_date.strftime('%d.%m.%Y')}"
                ))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()

    def get_selected_id(self):
        """Получить ID выбранной строки"""
        row = self.tableWidget.currentRow()
        if row >= 0:
            return int(self.tableWidget.item(row, 0).text())
        return None

    def add_item(self):
        """Добавить новый элемент"""
        if self.current_mode == "suppliers":
            dialog = SupplierDialog()
        elif self.current_mode == "contracts":
            dialog = ContractDialog()
        else:
            dialog = LicenseDialog()

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
            db = SessionLocal()
            try:
                if self.current_mode == "suppliers":
                    success = delete_supplier(db, item_id)
                elif self.current_mode == "contracts":
                    success = delete_contract(db, item_id)
                else:
                    success = delete_license(db, item_id)

                if success:
                    QMessageBox.information(self, "Успех", "Элемент удален")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить (элемент не найден)")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
            finally:
                db.close()


class SupplierDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Новый поставщик")
        self.setGeometry(200, 200, 300, 200)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.details_input = QLineEdit()

        layout.addRow("Название:", self.name_input)
        layout.addRow("Контакты:", self.contact_input)
        layout.addRow("Реквизиты:", self.details_input)

        btn_save = QPushButton("💾 Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)

        self.setLayout(layout)

    def save(self):
        db = SessionLocal()
        try:
            supplier = create_supplier(
                db,
                name=self.name_input.text(),
                contact_info=self.contact_input.text(),
                details=self.details_input.text()
            )
            QMessageBox.information(self, "Успех", f"Поставщик создан (ID: {supplier.id})")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()


class ContractDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Новый контракт")
        self.setGeometry(200, 200, 350, 250)

        layout = QFormLayout()

        self.supplier_id = QSpinBox()
        self.supplier_id.setRange(1, 10000)

        self.title = QLineEdit()

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addMonths(6))

        layout.addRow("ID поставщика:", self.supplier_id)
        layout.addRow("Название:", self.title)
        layout.addRow("Дата начала:", self.start_date)
        layout.addRow("Дата окончания:", self.end_date)

        btn_save = QPushButton("💾 Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)

        self.setLayout(layout)

    def save(self):
        db = SessionLocal()
        try:
            contract = create_contract(
                db,
                supplier_id=self.supplier_id.value(),
                title=self.title.text(),
                start_date_str=self.start_date.date().toString("yyyy-MM-dd"),
                end_date_str=self.end_date.date().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "Успех", f"Контракт создан (ID: {contract.id})")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()


class LicenseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Новая лицензия")
        self.setGeometry(200, 200, 350, 300)

        layout = QFormLayout()

        self.supplier_id = QSpinBox()
        self.supplier_id.setRange(1, 10000)

        self.contract_id = QSpinBox()
        self.contract_id.setRange(1, 10000)

        self.film_title = QLineEdit()
        self.digital_key = QLineEdit()

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addMonths(3))

        layout.addRow("ID поставщика:", self.supplier_id)
        layout.addRow("ID контракта:", self.contract_id)
        layout.addRow("Название фильма:", self.film_title)
        layout.addRow("Цифровой ключ:", self.digital_key)
        layout.addRow("Дата начала:", self.start_date)
        layout.addRow("Дата окончания:", self.end_date)

        btn_save = QPushButton("💾 Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)

        self.setLayout(layout)

    def save(self):
        db = SessionLocal()
        try:
            license_obj = create_license(
                db,
                supplier_id=self.supplier_id.value(),
                contract_id=self.contract_id.value(),
                film_title=self.film_title.text(),
                digital_key=self.digital_key.text(),
                start_date_str=self.start_date.date().toString("yyyy-MM-dd"),
                end_date_str=self.end_date.date().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "Успех", f"Лицензия создана (ID: {license_obj.id})")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            db.close()

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
            db = SessionLocal()
            try:
                if self.current_mode == "suppliers":
                    success = delete_supplier(db, item_id)
                elif self.current_mode == "contracts":
                    success = delete_contract(db, item_id)
                else:
                    success = delete_license(db, item_id)

                if success:
                    QMessageBox.information(self, "Успех", "Элемент удален")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить (элемент не найден)")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
            finally:
                db.close()
                