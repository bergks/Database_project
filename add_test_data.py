# add_test_data.py
from database import db
from datetime import date


def add_test_data():
    """Добавляет тестовые данные в базу данных"""
    try:
        print("Добавление тестовых данных...")

        # 1. Добавляем тестовые эксперименты
        experiments = [
            ("LLM2", "v7.2", "dataset1", date(2025, 1, 2), "Эксперимент по обнаружению DDoS атак"),
            ("CNN", "v1.0", "dataset2", date(2025, 1, 3), "Тестирование на синтетических данных"),
            ("RNN", "v2.1", "dataset3", date(2025, 1, 4), "Эксперимент с временными рядами"),
            ("Transformer", "v3.5", "dataset1", date(2025, 1, 5), "Сравнение с baseline моделями"),
            ("LLM2", "v7.3", "dataset4", date(2025, 1, 6), "Улучшенная версия модели"),
        ]

        experiment_ids = []
        for exp in experiments:
            exp_id = db.insert_experiment(exp[0], exp[1], exp[2], exp[3].isoformat(), exp[4])
            experiment_ids.append(exp_id)
            print(f"Добавлен эксперимент: {exp[0]} {exp[1]} (ID: {exp_id})")

        # 2. Добавляем тестовые параметры
        parameters = [
            (1, "learning_rate", "0.001"),
            (1, "batch_size", "32"),
            (1, "epochs", "100"),
            (2, "learning_rate", "0.01"),
            (2, "optimizer", "adam"),
            (3, "hidden_layers", "3"),
            (3, "neurons_per_layer", "128"),
            (4, "dropout_rate", "0.2"),
            (5, "learning_rate", "0.005"),
            (5, "activation", "relu"),
        ]

        for param in parameters:
            # Корректируем experiment_id относительно добавленных экспериментов
            actual_exp_id = experiment_ids[param[0] - 1] if param[0] <= len(experiment_ids) else param[0]
            db.insert_parameter(actual_exp_id, param[1], param[2])
        print("Добавлены параметры экспериментов")

        # 3. Добавляем тестовые метрики
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
            # Корректируем experiment_id
            actual_exp_id = experiment_ids[metric[0] - 1] if metric[0] <= len(experiment_ids) else metric[0]
            db.insert_metric(actual_exp_id, metric[1], metric[2], metric[3], metric[4])
        print("Добавлены метрики экспериментов")

        print("✅ Тестовые данные успешно добавлены!")

        # Показать итоговую статистику
        print("\nИтоговая статистика:")
        experiments_count = len(db.get_all_experiments())
        parameters_count = len(db.get_all_parameters())
        metrics_count = len(db.get_all_metrics())
        attacks_count = len(db.get_all_attack_types())

        print(f"Экспериментов: {experiments_count}")
        print(f"Параметров: {parameters_count}")
        print(f"Метрик: {metrics_count}")
        print(f"Типов атак: {attacks_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых данных: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    add_test_data()