from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QLabel)
from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtCore import Qt
from database import db
import logging


class HistoryWindow(QMainWindow):
    def __init__(self, parent=None, content_type="Эксперименты"):
        super().__init__(parent)
        self.setWindowTitle(f"Просмотр: {content_type}")
        self.resize(1200, 700)
        self.setMinimumSize(1000, 600)
        self.center_on_screen()
        self.content_type = content_type

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        if content_type == "Эксперименты":
            title_text = "Таблица экспериментов"
        elif content_type == "Метрики":
            title_text = "Таблица метрик"
        elif content_type == "Параметры":
            title_text = "Таблица параметров"
        else:
            title_text = f"Таблица {content_type.lower()}"

        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # Создаем соответствующую таблицу
        if content_type == "Эксперименты":
            self.setup_experiments_table(layout)
        elif content_type == "Метрики":
            self.setup_metrics_table(layout)
        elif content_type == "Параметры":
            self.setup_parameters_table(layout)

    def load_experiments_data(self):
        """Загружает данные экспериментов из базы данных"""
        try:
            experiments_data = db.get_all_experiments()

            # Преобразуем данные для таблицы
            table_data = []
            for exp in experiments_data:
                table_data.append([
                    exp['id'],
                    exp['model_name'],
                    exp['model_version'],
                    exp['dataset_name'],
                    exp['test_date'].strftime('%Y-%m-%d'),
                    exp['experiment_status_enum'],
                    exp['description'] or ''
                ])

            self.fill_table(table_data)

        except Exception as e:
            logging.error(f"Ошибка загрузки экспериментов: {e}")
            """experiments_data = [
                [1, "LLM2", "v7.2", "dataset1", "2025-01-02", "Ошибка загрузки данных"],
            ]
            self.fill_table(experiments_data)"""
            self.fill_table([])


    def load_metrics_data(self):
        """Загружает данные метрик из базы данных"""
        try:
            metrics_data = db.get_all_metrics()

            table_data = []
            for metric in metrics_data:
                table_data.append([
                    metric['id'],
                    metric['experiment_id'],
                    metric['attack_id'],
                    f"{metric['accuracy']:.3f}",
                    f"{metric['precision']:.3f}",
                    f"{metric['recall']:.3f}"
                ])

            self.fill_table(table_data)

        except Exception as e:
            logging.error(f"Ошибка загрузки метрик: {e}")
            self.fill_table([])

    def load_parameters_data(self):
        """Загружает данные параметров из базы данных"""
        try:
            parameters_data = db.get_all_parameters()

            table_data = []
            for param in parameters_data:
                table_data.append([
                    param['id'],
                    param['experiment_id'],
                    param['parameter_name'],
                    param['parameter_value']
                ])

            self.fill_table(table_data)

        except Exception as e:
            logging.error(f"Ошибка загрузки параметров: {e}")
            self.fill_table([])

    def setup_experiments_table(self, layout):
        """Создает таблицу экспериментов"""
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        headers = ["ID", "Модель", "Версия модели", "Датасет", "Дата", "Статус", "Описание"]
        self.table.setHorizontalHeaderLabels(headers)

        self.style_table()
        self.load_experiments_data()
        layout.addWidget(self.table)

    def setup_metrics_table(self, layout):
        """Создает таблицу метрик"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        headers = ["ID", "ID экспер.", "ID атаки", "Accuracy", "Precision", "Recall"]
        self.table.setHorizontalHeaderLabels(headers)

        self.style_table()
        self.load_metrics_data()
        layout.addWidget(self.table)

    def setup_parameters_table(self, layout):
        """Создает таблицу параметров"""
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        headers = ["ID", "ID экспер.", "Название", "Значение"]
        self.table.setHorizontalHeaderLabels(headers)

        self.style_table()
        self.load_parameters_data()
        layout.addWidget(self.table)

    def style_table(self):
        """Настраивает общий стиль таблицы"""
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #e6e6fa;
                padding: 8px;
                border: 1px solid #d8bfd8;
                font-weight: bold;
            }
        
        """)

    def fill_table(self, data):
        """Заполняет таблицу данными"""
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)  # ВСЕ ячейки по центру
                self.table.setItem(row, col, item)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            if col in [0, 1, 2]:
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QHeaderView.Stretch)

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)