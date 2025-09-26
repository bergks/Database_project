from database import db
import logging
from add_test_data import add_test_data

logging.basicConfig(level=logging.DEBUG)

def init_database():
    """инициализируем базу данных начальными данными"""
    try:
        initial_attacks = ["DDoS", "Brute Force", "SQL Injection", "Phishing", "Malware"]

        existing_attacks = db.get_all_attack_types()
        existing_names = [at['name'] for at in existing_attacks]

        for attack_name in initial_attacks:
            if attack_name not in existing_names:
                db.insert_attack_type(attack_name)
            else:
                print(f"Тип атаки '{attack_name}' уже существует")

        print("База данных инициализирована успешно!")
        add_test_data()

    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        import traceback
        traceback.print_exc()

def insert_attack_type(self, name: str) -> int:
    query = "INSERT INTO attack_types (name) VALUES (%s) RETURNING id"
    try:
        result = self.execute_query(query, (name,), fetch=True)
        if result and len(result) > 0:
            return result[0]['id']
        else:
            raise Exception("Не удалось получить ID созданного типа атаки")
    except Exception as e:
        logging.error(f"Ошибка при вставке типа атаки: {e}")
        raise e

if __name__ == "__main__":
    init_database()