import logging
from database import db
from datetime import date
from logging_config import configure_logging

configure_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def add_test_data():
    try:
        logging.info("Добавление тестовых данных...")

        experiments = [
            ("LLM2", "v7.2", "dataset1", date(2025, 1, 2), 'active', "Эксперимент по обнаружению DDoS атак"),
            ("CNN", "v1.0", "dataset2", date(2025, 1, 3), 'failed', "Тестирование на синтетических данных"),
            ("RNN", "v2.1", "dataset3", date(2025, 1, 4), 'completed',"Эксперимент с временными рядами"),
            ("Transformer", "v3.5", "dataset1", date(2025, 1, 5), 'completed', "Сравнение с baseline моделями"),
            ("LLM2", "v7.3", "dataset4", date(2025, 1, 6), 'active', "Улучшенная версия модели"),
        ]

        experiment_ids = []
        for exp in experiments:
            exp_id = db.insert_experiment(exp[0], exp[1], exp[2], exp[3].isoformat(), exp[4], exp[5])
            experiment_ids.append(exp_id)

        parameters = [
            (1, "learning_rate", "0.001"),
            (1, "batch_size", "32"),
            (1, "epochs", "100"),
            (2, "learning_rate", "0.01"),
            (2, "optimizer", "1"),
            (3, "hidden_layers", "3"),
            (3, "neurons_per_layer", "128"),
            (4, "dropout_rate", "0.2"),
            (5, "learning_rate", "0.005"),
            (5, "activation", "2"),
        ]

        for param in parameters:
            actual_exp_id = experiment_ids[param[0] - 1] if param[0] <= len(experiment_ids) else param[0]
            db.insert_parameter(actual_exp_id, param[1], param[2])

        metrics = [
            (1, 1, 0.95, 0.93, 0.92),
            (1, 2, 0.87, 0.85, 0.89),
            (2, 1, 0.91, 0.88, 0.90),
            (2, 3, 0.82, 0.80, 0.84),
            (3, 2, 0.89, 0.87, 0.91),
            (4, 1, 0.94, 0.92, 0.93),
            (5, 3, 0.85, 0.83, 0.86),
        ]

        for metric in metrics:
            actual_exp_id = experiment_ids[metric[0] - 1] if metric[0] <= len(experiment_ids) else metric[0]
            db.insert_metric(actual_exp_id, metric[1], metric[2], metric[3], metric[4])

        logging.info("Тестовые данные успешно добавлены!")

    except Exception as e:
        logging.error(f"Ошибка при добавлении тестовых данных: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    add_test_data()