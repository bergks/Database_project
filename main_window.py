from PySide6.QtWidgets import (QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel)
from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtCore import Qt
from add_experiment_dialog import AddExperimentDialog
from add_attack_type_dialog import AddAttackTypeDialog
from history_window import HistoryWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Моя база данных")
        self.resize(700, 500)
        self.setMinimumSize(600, 400)
        self.center_window()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)

        layout.setContentsMargins(180, 30, 180, 30)  # ← left, top, right, bottom

        title_label = QLabel("Моя база данных")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)

        self.btn_add_exp = QPushButton("Добавить новый эксперимент")
        self.btn_add_attack = QPushButton("Посмотреть/Добавить типы атак")

        self.btn_view_experiments = QPushButton("Посмотреть эксперименты")
        self.btn_view_metrics = QPushButton("Посмотреть метрики")
        self.btn_view_params = QPushButton("Посмотреть параметры")

        all_buttons = [
            self.btn_add_exp,
            self.btn_add_attack,
            self.btn_view_experiments,
            self.btn_view_metrics,
            self.btn_view_params
        ]

        # Настраиваем кнопки с светло-сиреневым цветом
        for button in all_buttons:
            button.setMinimumHeight(45)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #e6e6fa;
                    color: #2c3e50;
                    border: 2px solid #d8bfd8;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #d8bfd8;
                    border: 2px solid #c9a0c9;
                }
                QPushButton:pressed {
                    background-color: #c9a0c9;
                    border: 2px solid #ba81ba;
                }
            """)

        layout.addWidget(self.btn_add_exp)
        layout.addWidget(self.btn_add_attack)
        layout.addWidget(QLabel())  # Пустой отступ

        layout.addWidget(self.btn_view_experiments)
        layout.addWidget(self.btn_view_metrics)
        layout.addWidget(self.btn_view_params)

        self.btn_add_exp.clicked.connect(self.open_add_experiment)
        self.btn_add_attack.clicked.connect(self.open_attack_types)
        self.btn_view_experiments.clicked.connect(self.open_experiments_view)
        self.btn_view_metrics.clicked.connect(self.open_metrics_view)
        self.btn_view_params.clicked.connect(self.open_params_view)

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def open_add_experiment(self):
        dialog = AddExperimentDialog(self)
        dialog.exec()

    def open_attack_types(self):
        dialog = AddAttackTypeDialog(self)
        dialog.exec()

    def open_experiments_view(self):
        window = HistoryWindow(self, "Эксперименты")
        window.show()
        window.activateWindow()

    def open_metrics_view(self):
        window = HistoryWindow(self, "Метрики")
        window.show()
        window.activateWindow()

    def open_params_view(self):
        window = HistoryWindow(self, "Параметры")
        window.show()
        window.activateWindow()