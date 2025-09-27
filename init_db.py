from database import db
import logging
from add_test_data import add_test_data
from logging_config import configure_logging

logger = logging.getLogger(__name__)

def init_database():
    db.init_db()
    """Инициализирует базу данных начальными данными"""
    try:
        initial_attacks = ["DDoS", "Brute Force", "SQL Injection", "Phishing", "Malware"]

        existing_attacks = db.get_all_attack_types()
        existing_names = [at['name'] for at in existing_attacks]

        for attack_name in initial_attacks:
            if attack_name not in existing_names:
                db.insert_attack_type(attack_name)
                logger.info(f"Добавлен тип атаки: {attack_name}")
            else:
                logger.warning(f"Тип атаки '{attack_name}' уже существует")

        final_attacks = db.get_all_attack_types()
        logger.info(f"Итоговое количество типов атак: {len(final_attacks)}")
        for attack in final_attacks:
            logger.info(f"ID: {attack['id']}, Name: {attack['name']}")

        logger.info("База данных инициализирована успешно!")
        add_test_data()

    except Exception as e:
        logger.debug(f"Ошибка инициализации БД: {e}")
        import traceback
        traceback.print_exc()

def insert_attack_type(self, name: str) -> int:
    """Добавляет новый тип атаки"""
    query = "INSERT INTO attack_types (name) VALUES (%s) RETURNING id"
    try:
        result = self.execute_query(query, (name,), fetch=True)
        if result and len(result) > 0:
            logger.info(f"Атака {name} успешно добавлена")
            return result[0]['id']
        else:
            raise Exception("Не удалось получить ID созданного типа атаки")
    except Exception as e:
        logging.error(f"Ошибка при вставке типа атаки: {e}")
        raise e

if __name__ == "__main__":
    init_database()