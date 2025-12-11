# ОСНОВНОЙ ФАЙЛ ДЛЯ ЗАПУСКА PYQT ПРОГРАММЫ
import sys
import traceback

from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from database import init_db

def excepthook(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"Критическая ошибка:\n{error_msg}")
    with open("error.log", "a") as f:
        f.write(error_msg + "\n\n")


def main():
    sys.excepthook = excepthook

    # Инициализация базы данных
    try:
        init_db()
        print("База данных инициализирована")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")

    app = QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()