# UI ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ИНТЕРФЕЙСА УВЕМЕДОМЛЕНИЯ
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                            QLabel, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.license_service import get_expiring_contracts, get_expiring_licenses
from services.supplier_service import get_supplier_by_id

class NotificationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.init_ui()
        self.load_notifications()
        
    def init_ui(self):
        self.setWindowTitle("Уведомления")
        self.setGeometry(300, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Уведомления системы")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        self.notifications_list = QListWidget()
        layout.addWidget(self.notifications_list)
        
        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 5px;
            }
        """

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_notifications)
        self.refresh_button.setStyleSheet(button_style)
        
        layout.addWidget(self.refresh_button)
        
        self.setLayout(layout)
        
    def load_notifications(self):
        """Загрузка уведомлений о заканчивающихся лицензиях и контрактах"""
        self.notifications_list.clear()
        
        try:
            notifications = []
            
            # 1. Проверка заканчивающихся контрактов (30 дней)
            expiring_contracts = get_expiring_contracts(self.db, 30)
            for contract in expiring_contracts:
                supplier = get_supplier_by_id(self.db, contract['supplier_id'])
                supplier_name = supplier.name if supplier else f"ID: {contract['supplier_id']}"
                
                days_text = "сегодня" if contract['days_until_expiry'] == 0 else f"через {contract['days_until_expiry']} дней"
                
                notifications.append({
                    'type': 'contract',
                    'title': f'Контракт заканчивается {days_text}',
                    'message': f"Контракт '{contract['title']}' с поставщиком '{supplier_name}'",
                    'end_date': contract['end_date'],
                    'days': contract['days_until_expiry']
                })
            
            # 2. Проверка заканчивающихся лицензий (30 дней)
            expiring_licenses = get_expiring_licenses(self.db, 30)
            for license in expiring_licenses:
                days_text = "сегодня" if license['days_until_expiry'] == 0 else f"через {license['days_until_expiry']} дней"
                
                notifications.append({
                    'type': 'license',
                    'title': f'Лицензия заканчивается {days_text}',
                    'message': f"Лицензия на фильм '{license['film_title']}'",
                    'end_date': license['end_date'],
                    'days': license['days_until_expiry']
                })
            
            # Сортируем по количеству оставшихся дней
            notifications.sort(key=lambda x: x['days'])
            
            # Отображаем уведомления
            if not notifications:
                item = QListWidgetItem("Нет уведомлений")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.notifications_list.addItem(item)
            else:
                for notification in notifications:
                    item_text = f"{notification['title']}\n{notification['message']}"
                    item = QListWidgetItem(item_text)
                    self.notifications_list.addItem(item)
                    
        except Exception as e:
            error_item = QListWidgetItem(f"Ошибка загрузки уведомлений: {str(e)}")
            self.notifications_list.addItem(error_item)
