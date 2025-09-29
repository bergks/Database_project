from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QLabel, QComboBox, QPushButton)
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
        self.all_experiments_data = []
        self.filtered_experiments_data = []

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

        # Добавляем панель фильтров только для экспериментов
        if content_type == "Эксперименты":
            self.setup_filter_panel(layout)

        # Создаем соответствующую таблицу
        if content_type == "Эксперименты":
            self.setup_experiments_table(layout)
        elif content_type == "Метрики":
            self.setup_metrics_table(layout)
        elif content_type == "Параметры":
            self.setup_parameters_table(layout)

    def setup_filter_panel(self, layout):
        """Создает панель фильтров для экспериментов"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 10)

        # Метка фильтра
        filter_label = QLabel("Фильтр по статусу:")
        filter_label.setFont(QFont("Arial", 10, QFont.Bold))
        filter_label.setStyleSheet("color: #2c3e50; min-width: 120px;")
        filter_layout.addWidget(filter_label)

        # Выпадающий список статусов
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("Все статусы", "all")
        self.status_filter_combo.addItem("Активные", "active")
        self.status_filter_combo.addItem("Завершенные", "completed")
        self.status_filter_combo.addItem("Неудачные", "failed")

        self.status_filter_combo.setFixedHeight(30)
        self.status_filter_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #d8bfd8;
                border-radius: 4px;
                font-size: 11px;
                background-color: white;
                color: black
            }
            QComboBox:focus {
                border: 1px solid #c9a0c9;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        filter_layout.addWidget(self.status_filter_combo)

        # Кнопка сброса фильтра
        self.reset_filter_btn = QPushButton("Сбросить фильтр")
        self.reset_filter_btn.setFixedHeight(30)
        self.reset_filter_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: bold;
                background-color: #e6e6fa;
                color: #2c3e50;
                border: 1px solid #d8bfd8;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d8bfd8;
            }
            QPushButton:pressed {
                background-color: #c9a0c9;
            }
        """)
        filter_layout.addWidget(self.reset_filter_btn)

        filter_layout.addStretch()

        # Подключаем сигналы
        self.status_filter_combo.currentIndexChanged.connect(self.apply_status_filter)
        self.reset_filter_btn.clicked.connect(self.reset_filter)

        layout.addWidget(filter_widget)

    def apply_status_filter(self):
        """Применяет фильтр по статусу"""
        if self.content_type != "Эксперименты":
            return

        selected_status = self.status_filter_combo.currentData()

        if selected_status == "all":
            self.filtered_experiments_data = self.all_experiments_data.copy()
        else:
            self.filtered_experiments_data = [
                exp for exp in self.all_experiments_data
                if exp[5].lower() == selected_status.lower()
            ]

        self.fill_table(self.filtered_experiments_data)

        # Обновляем информацию о количестве записей
        self.update_records_count()

    def reset_filter(self):
        """Сбрасывает фильтр"""
        if self.content_type != "Эксперименты":
            return

        self.status_filter_combo.setCurrentIndex(0)  # "Все статусы"
        self.filtered_experiments_data = self.all_experiments_data.copy()
        self.fill_table(self.filtered_experiments_data)
        self.update_records_count()

    def update_records_count(self):
        """Обновляет информацию о количестве записей"""
        if hasattr(self, 'records_label'):
            total_count = len(self.all_experiments_data)
            filtered_count = len(self.filtered_experiments_data)

            if total_count == filtered_count:
                self.records_label.setText(f"Всего записей: {total_count}")
            else:
                self.records_label.setText(f"Показано: {filtered_count} из {total_count} записей")

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

            self.all_experiments_data = table_data
            self.filtered_experiments_data = table_data.copy()
            self.fill_table(self.filtered_experiments_data)

            # Добавляем информацию о количестве записей
            if hasattr(self, 'records_label'):
                self.records_label.setText(f"Всего записей: {len(table_data)}")
            else:
                # Создаем метку для отображения количества записей
                self.records_label = QLabel(f"Всего записей: {len(table_data)}")
                self.records_label.setFont(QFont("Arial", 9))
                self.records_label.setStyleSheet("color: #666; font-style: italic;")
                self.records_label.setAlignment(Qt.AlignRight)

                # Добавляем метку в layout (после таблицы)
                layout = self.centralWidget().layout()
                layout.addWidget(self.records_label)

        except Exception as e:
            logging.error(f"Ошибка загрузки экспериментов: {e}")
            self.all_experiments_data = []
            self.filtered_experiments_data = []
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
                    metric.get('attack_name', metric['attack_id']),  # Используем имя атаки если есть
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
        headers = ["ID", "ID экспер.", "Тип атаки", "Accuracy", "Precision", "Recall"]
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
                font-size: 10px;
                color: black;
            }
            QHeaderView::section {
                background-color: #e6e6fa;
                padding: 8px;
                color: black;
                border: 1px solid #d8bfd8;
                font-weight: bold;
                font-size: 10px;
            }

            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
                background-color: white
            }
            
        """)

    def fill_table(self, data):
        """Заполняет таблицу данными"""
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row, col, item)

        # Настройка размеров колонок
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            if col in [0, 1, 2, 4]:  # ID, Модель, Версия, Дата - фиксированный размер
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QHeaderView.Stretch)

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)