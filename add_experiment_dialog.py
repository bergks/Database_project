from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QDateEdit, QTextEdit, QComboBox,
                               QPushButton, QFrame, QWidget,
                               QDoubleSpinBox, QMessageBox, QGridLayout)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDate
from database import db
import logging

from logging_config import configure_logging

configure_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AddExperimentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новый эксперимент")
        self.setModal(True)
        self.setFixedSize(650, 840)
        self.center_on_parent()

        self.status_types = [("active", "Активный"), ("completed", "Завершен"), ("failed", "Неудачный")]
        self.attack_types = []
        self.setup_ui()

        self.load_attack_types()

    def center_on_parent(self):
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        title_label = QLabel("Добавление нового эксперимента")
        title_label.setFont(QFont("Arial", 13, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        main_layout.addWidget(title_label)

        main_info_group = self.create_main_info_group()
        main_layout.addWidget(main_info_group)

        self.parameters_widget = self.create_parameters_widget()
        main_layout.addWidget(self.parameters_widget)

        self.metrics_widget = self.create_metrics_widget()
        main_layout.addWidget(self.metrics_widget)

        self.status_widget = self.create_status_widget()
        main_layout.addWidget(self.status_widget)

        bottom_widget = self.create_bottom_widget()
        main_layout.addWidget(bottom_widget)

    def create_main_info_group(self):
        group = QFrame()
        group.setFrameStyle(QFrame.Box)
        group.setStyleSheet("QFrame { border: 2px solid #d8bfd8; border-radius: 6px; padding: 10px; }")

        layout = QVBoxLayout(group)

        title = QLabel("Основная информация")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Сетка для полей ввода
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(12)
        grid_layout.setVerticalSpacing(6)

        # Поля ввода
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("Название модели")
        self.model_name_input.setFixedHeight(28)

        self.model_version_input = QLineEdit()
        self.model_version_input.setPlaceholderText("Версия модели")
        self.model_version_input.setFixedHeight(28)

        self.dataset_input = QLineEdit()
        self.dataset_input.setPlaceholderText("Название датасета")
        self.dataset_input.setFixedHeight(28)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setFixedHeight(28)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Описание эксперимента")
        self.description_input.setFixedHeight(28)
        self.description_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.description_input.setLineWrapMode(QTextEdit.WidgetWidth)

        input_style = """
            QLineEdit, QDateEdit {
                padding: 4px;
                border: 1px solid #d8bfd8;
                border-radius: 3px;
                font-size: 9px;
                min-height: 28px;
                max-height: 28px;
            }
            QTextEdit {
                padding: 4px;
                border: 1px solid #d8bfd8;
                border-radius: 3px;
                font-size: 9px;
                min-height: 28px;
                max-height: 28px;
            }
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #c9a0c9;
            }
        """

        self.model_name_input.setStyleSheet(input_style)
        self.model_version_input.setStyleSheet(input_style)
        self.dataset_input.setStyleSheet(input_style)
        self.date_input.setStyleSheet(input_style)
        self.description_input.setStyleSheet(input_style)

        label_style = "QLabel { font-size: 9px; font-weight: bold; color: #2c3e50; min-width: 110px; }"

        label1 = QLabel("Название модели:")
        label1.setStyleSheet(label_style)
        grid_layout.addWidget(label1, 0, 0)

        label2 = QLabel("Версия модели:")
        label2.setStyleSheet(label_style)
        grid_layout.addWidget(label2, 1, 0)

        label3 = QLabel("Название датасета:")
        label3.setStyleSheet(label_style)
        grid_layout.addWidget(label3, 2, 0)

        label4 = QLabel("Дата (ГГГГ-ММ-ДД):")
        label4.setStyleSheet(label_style)
        grid_layout.addWidget(label4, 3, 0)

        label5 = QLabel("Описание:")
        label5.setStyleSheet(label_style)
        grid_layout.addWidget(label5, 4, 0)

        grid_layout.addWidget(self.model_name_input, 0, 1)
        grid_layout.addWidget(self.model_version_input, 1, 1)
        grid_layout.addWidget(self.dataset_input, 2, 1)
        grid_layout.addWidget(self.date_input, 3, 1)
        grid_layout.addWidget(self.description_input, 4, 1)

        layout.addLayout(grid_layout)
        return group

    def create_parameters_widget(self):
        group = QFrame()
        group.setFrameStyle(QFrame.Box)
        group.setStyleSheet("QFrame { border: 2px solid #d8bfd8; border-radius: 6px; padding: 10px; }")

        layout = QVBoxLayout(group)

        header_layout = QHBoxLayout()
        title = QLabel("Параметры модели")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.parameters_container = QVBoxLayout()
        self.parameters_container.setSpacing(6)
        layout.addLayout(self.parameters_container)

        self.add_parameter_row()

        return group

    def create_metrics_widget(self):
        group = QFrame()
        group.setFrameStyle(QFrame.Box)
        group.setStyleSheet("QFrame { border: 2px solid #d8bfd8; border-radius: 6px; padding: 10px; }")

        layout = QVBoxLayout(group)

        header_layout = QHBoxLayout()
        title = QLabel("Метрики")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.metrics_container = QVBoxLayout()
        self.metrics_container.setSpacing(6)
        layout.addLayout(self.metrics_container)

        self.add_metric_row()

        return group

    def create_status_widget(self):
        group = QFrame()
        group.setFrameStyle(QFrame.Box)
        group.setStyleSheet("QFrame { border: 2px solid #d8bfd8; border-radius: 6px; padding: 10px; }")

        layout = QVBoxLayout(group)

        header_layout = QHBoxLayout()
        title = QLabel("Статус эксперимента")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.status_container = QVBoxLayout()
        self.status_container.setSpacing(6)
        layout.addLayout(self.status_container)

        self.add_status_row()

        return group

    def create_bottom_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.status_label = QLabel("Статус: не сохранено")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        layout.addWidget(self.status_label)

        self.save_btn = QPushButton("Сохранить эксперимент")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.setStyleSheet(self.get_save_button_style())
        self.save_btn.clicked.connect(self.save_experiment)
        layout.addWidget(self.save_btn)

        return widget

    def add_parameter_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Название параметра")
        name_input.setFixedHeight(26)
        name_input.setStyleSheet("""
            QLineEdit { 
                padding: 4px; 
                border: 1px solid #d8bfd8; 
                border-radius: 3px; 
                font-size: 9px;
                min-height: 26px;
                max-height: 26px;
            }
            QLineEdit:focus {
                border: 1px solid #c9a0c9;
            }
        """)

        value_input = QDoubleSpinBox()
        value_input.setRange(-999999.999, 999999.999)
        value_input.setSingleStep(0.01)
        value_input.setDecimals(3)
        value_input.setValue(0.0)
        value_input.setFixedHeight(26)
        value_input.setStyleSheet("""
            QDoubleSpinBox { 
                padding: 4px; 
                border: 1px solid #d8bfd8; 
                border-radius: 3px; 
                font-size: 9px;
                min-height: 26px;
                max-height: 26px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #c9a0c9;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 15px;
                background-color: #e6e6fa;
                border: 1px solid #d8bfd8;
                border-radius: 2px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #d8bfd8;
            }
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                width: 8px;
                height: 8px;
            }
        """)

        small_label_style = "QLabel { font-size: 8px; font-weight: bold; color: #2c3e50; min-width: 50px; }"

        name_label = QLabel("Название:")
        name_label.setStyleSheet(small_label_style)
        row_layout.addWidget(name_label)
        row_layout.addWidget(name_input)

        value_label = QLabel("Значение:")
        value_label.setStyleSheet(small_label_style)
        row_layout.addWidget(value_label)
        row_layout.addWidget(value_input)

        self.parameters_container.addWidget(row_widget)

    def add_metric_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        attack_combo = QComboBox()
        if hasattr(self, 'attack_types') and self.attack_types:
            for attack_name, attack_id in self.attack_types:
                attack_combo.addItem(attack_name, attack_id)
        attack_combo.setFixedHeight(26)
        attack_combo.setStyleSheet("""
            QComboBox { 
                padding: 4px; 
                border: 1px solid #d8bfd8; 
                border-radius: 3px; 
                font-size: 9px;
                min-height: 26px;
                max-height: 26px;
                min-width: 80px;
            }
            QComboBox:focus {
                border: 1px solid #c9a0c9;
            }
        """)

        accuracy_input = QDoubleSpinBox()
        accuracy_input.setRange(0, 1)
        accuracy_input.setSingleStep(0.01)
        accuracy_input.setDecimals(3)
        accuracy_input.setValue(0.0)
        accuracy_input.setPrefix("A:")
        accuracy_input.setFixedHeight(26)
        accuracy_input.setStyleSheet("QDoubleSpinBox { font-size: 8px; min-width: 60px; }")

        precision_input = QDoubleSpinBox()
        precision_input.setRange(0, 1)
        precision_input.setSingleStep(0.01)
        precision_input.setDecimals(3)
        precision_input.setValue(0.0)
        precision_input.setPrefix("P:")
        precision_input.setFixedHeight(26)
        precision_input.setStyleSheet("QDoubleSpinBox { font-size: 8px; min-width: 60px; }")

        recall_input = QDoubleSpinBox()
        recall_input.setRange(0, 1)
        recall_input.setSingleStep(0.01)
        recall_input.setDecimals(3)
        recall_input.setValue(0.0)
        recall_input.setPrefix("R:")
        recall_input.setFixedHeight(26)
        recall_input.setStyleSheet("QDoubleSpinBox { font-size: 8px; min-width: 60px; }")

        small_label_style = "QLabel { font-size: 8px; font-weight: bold; color: #2c3e50; min-width: 45px; }"

        attack_label = QLabel("Атака:")
        attack_label.setStyleSheet(small_label_style)
        row_layout.addWidget(attack_label)
        row_layout.addWidget(attack_combo)
        row_layout.addWidget(accuracy_input)
        row_layout.addWidget(precision_input)
        row_layout.addWidget(recall_input)

        self.metrics_container.addWidget(row_widget)

    def add_status_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        self.status_combo = QComboBox()  # Сохраняем как атрибут для доступа из других методов
        for status_key, status_name in self.status_types:
            self.status_combo.addItem(status_name, status_key)

        self.status_combo.setFixedHeight(26)
        self.status_combo.setStyleSheet("""
            QComboBox { 
                padding: 4px; 
                border: 1px solid #d8bfd8; 
                border-radius: 3px; 
                font-size: 9px;
                min-height: 26px;
                max-height: 26px;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 1px solid #c9a0c9;
            }
        """)

        small_label_style = "QLabel { font-size: 9px; font-weight: bold; color: #2c3e50; min-width: 120px; }"

        status_label = QLabel("Статус эксперимента:")
        status_label.setStyleSheet(small_label_style)
        row_layout.addWidget(status_label)
        row_layout.addWidget(self.status_combo)
        row_layout.addStretch()

        self.status_container.addWidget(row_widget)

    def get_save_button_style(self):
        return """
            QPushButton {
                font-size: 11px;
                font-weight: bold;
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """

    def validation(self, data):
        if not data['model_name'] or not data['model_version'] or not data['dataset_name']:
            logging.warning('Заполнены не все обязательные поля')
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля: модель, версия, датасет!")
            return False

        if len(data['model_name']) > 50:
            logging.warning('Имя модели должно быть меньше 50 символов')
            QMessageBox.warning(self, "Ошибка", "Имя модели должно быть меньше 50 символов")
            return False

        if len(data['model_version']) > 10:
            logging.warning('Версия модели должна быть меньше 10 символов')
            QMessageBox.warning(self, "Ошибка", "Версия модели должна быть меньше 10 символов")
            return False

        if len(data['dataset_name']) > 50:
            logging.warning("Имя датасета должно быть меньше 50 символов")
            QMessageBox.warning(self, "Ошибка", "Имя датасета должно быть меньше 50 символов")
            return False

        if len(data['parameters'][0]['name']) > 50:
            logging.warning("Имя параметра должно быть меньше 50 символов")
            QMessageBox.warning(self, "Ошибка", "Имя параметра должно быть меньше 50 символов")
            return False


    def collect_experiment_data(self):
        """собираем параметры"""
        data = {
            'model_name': self.model_name_input.text(),
            'model_version': self.model_version_input.text(),
            'dataset_name': self.dataset_input.text(),
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'description': self.description_input.toPlainText(),
            'status': self.status_combo.currentData(),  # Берем статус из комбобокса
            'status_text': self.status_combo.currentText(),
            'parameters': [],
            'metrics': []
        }

        for i in range(self.parameters_container.count()):
            widget = self.parameters_container.itemAt(i).widget()
            if widget:
                line_edits = widget.findChildren(QLineEdit)
                spin_boxes = widget.findChildren(QDoubleSpinBox)
                if line_edits and spin_boxes:
                    param_name = line_edits[0].text()
                    param_value = spin_boxes[0].value()
                    if param_name:
                        data['parameters'].append({
                            'name': param_name,
                            'value': param_value
                        })

        # Собираем метрики
        for i in range(self.metrics_container.count()):
            widget = self.metrics_container.itemAt(i).widget()
            if widget:
                combo = widget.findChild(QComboBox)
                spins = widget.findChildren(QDoubleSpinBox)
                if combo and len(spins) >= 3:
                    data['metrics'].append({
                        'attack_type_id': combo.currentData(),
                        'attack_type_name': combo.currentText(),
                        'accuracy': spins[0].value(),
                        'precision': spins[1].value(),
                        'recall': spins[2].value()
                    })

        logging.info("Данные добавлены в data")
        return data



    def load_attack_types(self):
        try:
            attack_types_data = db.get_all_attack_types()
            self.attack_types = [(at['name'], at['id']) for at in attack_types_data]

            self.update_attack_comboboxes()
            logging.info("Данные успешно загружены и обновлены")
        except Exception as e:
            logging.error(f"Ошибка загрузки типов атак: {e}")

    def update_attack_comboboxes(self):
        for i in range(self.metrics_container.count()):
            widget = self.metrics_container.itemAt(i).widget()
            if widget:
                combo = widget.findChild(QComboBox)
                if combo:
                    combo.clear()
                    for attack_name, attack_id in self.attack_types:
                        combo.addItem(attack_name, attack_id)

    def save_experiment(self):
        try:
            data = self.collect_experiment_data()

            if not self.validation(data):
                return

            experiment_id = db.insert_experiment(
                data['model_name'],
                data['model_version'],
                data['dataset_name'],
                data['date'],
                data['status'],
                data['description']
            )

            for param in data['parameters']:
                db.insert_parameter(experiment_id, param['name'], param['value'])

            for metric in data['metrics']:
                db.insert_metric(
                    experiment_id,
                    metric['attack_type_id'],
                    metric['accuracy'],
                    metric['precision'],
                    metric['recall']
                )

            QMessageBox.information(self, "Успех", f"Эксперимент #{experiment_id} сохранен!")
            self.status_label.setText("Статус: сохранено")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            logging.info("Данные успешно сохранены")

        except Exception as e:
            logging.error(f"Ошибка сохранения эксперимента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить эксперимент: {str(e)}")