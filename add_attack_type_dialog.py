from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox,
                               QWidget, QFrame)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from database import db
import logging


class AddAttackTypeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление типа атак")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.center_on_parent()
        self.attack_types = []
        self.setup_ui()
        self.load_attack_types()

    def load_attack_types(self):
        try:
            attack_types_data = db.get_all_attack_types()
            self.attack_types = [(at['id'], at['name']) for at in attack_types_data]
            self.load_attacks_data()
        except Exception as e:
            logging.error(f"Ошибка загрузки типов атак: {e}")
            self.load_attacks_data()

    def save_attack_type(self):
        attack_name = self.new_attack_input.text().strip()

        if not attack_name:
            QMessageBox.warning(self, "Ошибка", "Введите название типа атаки!")
            return

        try:
            """проверяем существование в базе данных"""
            existing_attacks = db.get_all_attack_types()
            existing_names = [at['name'] for at in existing_attacks]

            if attack_name in existing_names:
                QMessageBox.warning(self, "Ошибка", "Тип атаки с таким названием уже существует!")
                return

            """сохраняем в базу данных"""
            new_id = db.insert_attack_type(attack_name)

            """"обновляем локальный список и таблицу"""
            self.attack_types.append((new_id, attack_name))
            self.load_attacks_data()

            """очищаем поле ввода и обновляем статус"""
            self.new_attack_input.clear()
            self.status_label.setText("Статус: сохранено")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

            QMessageBox.information(self, "Успех", f"Тип атаки '{attack_name}' добавлен!")

        except Exception as e:
            logging.error(f"Ошибка сохранения типа атаки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить тип атаки: {str(e)}")


    def center_on_parent(self):
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)

    def setup_ui(self):
        """настраиваем интерфейс диалога"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Добавление типа атак")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        current_attacks_group = self.create_current_attacks_group()
        main_layout.addWidget(current_attacks_group)

        new_attack_group = self.create_new_attack_group()
        main_layout.addWidget(new_attack_group)

        """статус и кнопка сохранения"""
        bottom_widget = self.create_bottom_widget()
        main_layout.addWidget(bottom_widget)

    def create_current_attacks_group(self):
        group = QFrame()
        group.setFrameStyle(QFrame.Box)
        group.setStyleSheet("QFrame { border: 2px solid #d8bfd8; border-radius: 6px; padding: 10px; }")

        layout = QVBoxLayout(group)

        title = QLabel("Список текущих типов атак:")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        self.setup_attacks_table(layout)

        return group

    def setup_attacks_table(self, layout):
        """создаем и настраиваем таблицу типов атак"""
        self.attacks_table = QTableWidget()
        self.attacks_table.setColumnCount(2)
        self.attacks_table.setHorizontalHeaderLabels(["ID", "Название атаки"])

        self.attacks_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 10px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e6e6fa;
                padding: 8px;
                border: 1px solid #d8bfd8;
                font-weight: bold;
                font-size: 10px;
            }

            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
            }
        """)

        """настраиваем поведение колонок"""
        header = self.attacks_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.load_attacks_data()

        layout.addWidget(self.attacks_table)

    def load_attacks_data(self):
        self.attacks_table.setRowCount(len(self.attack_types))
        for row, (attack_id, attack_name) in enumerate(self.attack_types):
            id_item = QTableWidgetItem(str(attack_id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.attacks_table.setItem(row, 0, id_item)

            name_item = QTableWidgetItem(attack_name)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.attacks_table.setItem(row, 1, name_item)

    def create_new_attack_group(self):
        group = QFrame()
        group.setFrameStyle(QFrame.Box)
        group.setStyleSheet("QFrame { border: 2px solid #d8bfd8; border-radius: 6px; padding: 10px; }")

        layout = QVBoxLayout(group)

        title = QLabel("Новый тип атак")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        """поле ввода названия атаки"""
        input_layout = QHBoxLayout()

        name_label = QLabel("Название:")
        name_label.setFont(QFont("Arial", 9))
        name_label.setStyleSheet("color: #2c3e50; font-weight: bold; min-width: 70px;")
        input_layout.addWidget(name_label)

        self.new_attack_input = QLineEdit()
        self.new_attack_input.setPlaceholderText("Введите название нового типа атаки")
        self.new_attack_input.setFixedHeight(30)
        self.new_attack_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #d8bfd8;
                border-radius: 3px;
                font-size: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #c9a0c9;
            }
        """)
        input_layout.addWidget(self.new_attack_input)

        layout.addLayout(input_layout)

        return group

    def create_bottom_widget(self):
        """создаем нижнюю часть с кнопкой сохранения и статусом"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        self.status_label = QLabel("Статус: не сохранено")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        layout.addWidget(self.status_label)

        self.save_btn = QPushButton("Сохранить тип")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: bold;
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.save_btn.clicked.connect(self.save_attack_type)
        layout.addWidget(self.save_btn)

        return widget

    def update_status(self):
        self.status_label.setText("Статус: не сохранено")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")