import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from config import DB_CONFIG
import logging


class DatabaseManager:
    def __init__(self):
        self.connection_params = DB_CONFIG

    def get_connection(self):
        """устанавливаем соединение с базой данных"""
        return psycopg2.connect(**self.connection_params)

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """выполняем запрос к базе данных"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def insert_experiment(self, model_name: str, model_version: str, dataset_name: str,
                          test_date: str, description: str) -> int:
        query = """
        INSERT INTO experiments (model_name, model_version, dataset_name, test_date, description)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """
        """result = self.execute_query(query, (model_name, model_version, dataset_name, test_date, description),
                                    fetch=True)
        return result[0]['id']"""
        try:
            result = self.execute_query(query, (model_name, model_version, dataset_name, test_date, description),
                                        fetch=True)
            if result and len(result) > 0:
                return result[0]['id']
            else:
                raise Exception("Не удалось получить ID созданного эксперимента")
        except Exception as e:
            logging.error(f"Ошибка при вставке эксперимента: {e}")
            raise e

    def get_all_experiments(self) -> List[Dict]:
        query = "SELECT * FROM experiments ORDER BY id ASC"
        return self.execute_query(query, fetch=True)

    def get_experiment_by_id(self, experiment_id: int) -> Optional[Dict]:
        query = "SELECT * FROM experiments WHERE id = %s"
        result = self.execute_query(query, (experiment_id,), fetch=True)
        return result[0] if result else None

    def get_all_attack_types(self) -> List[Dict]:
        query = "SELECT * FROM attack_types ORDER BY id"
        return self.execute_query(query, fetch=True)

    def insert_attack_type(self, name: str) -> int:
        query = "INSERT INTO attack_types (name) VALUES (%s) RETURNING id"
        result = self.execute_query(query, (name,), fetch=True)
        return result[0]['id']

    def insert_parameter(self, experiment_id: int, parameter_name: str, parameter_value: str):
        query = """
        INSERT INTO parameters (experiment_id, parameter_name, parameter_value)
        VALUES (%s, %s, %s)
        """
        self.execute_query(query, (experiment_id, parameter_name, str(parameter_value)))

    def get_parameters_by_experiment(self, experiment_id: int) -> List[Dict]:
        query = "SELECT * FROM parameters WHERE experiment_id = %s"
        return self.execute_query(query, (experiment_id,), fetch=True)

    def insert_metric(self, experiment_id: int, attack_id: int, accuracy: float,
                      precision: float, recall: float):
        query = """
        INSERT INTO experiment_metrics (experiment_id, attack_id, accuracy, precision, recall)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_query(query, (experiment_id, attack_id, accuracy, precision, recall))

    def get_metrics_by_experiment(self, experiment_id: int) -> List[Dict]:
        query = """
        SELECT em.*, at.name as attack_name 
        FROM experiment_metrics em 
        LEFT JOIN attack_types at ON em.attack_id = at.id 
        WHERE em.experiment_id = %s
        """
        return self.execute_query(query, (experiment_id,), fetch=True)

    def get_all_metrics(self) -> List[Dict]:
        query = """
        SELECT em.*, e.model_name, at.name as attack_name 
        FROM experiment_metrics em 
        LEFT JOIN experiments e ON em.experiment_id = e.id 
        LEFT JOIN attack_types at ON em.attack_id = at.id 
        ORDER BY em.id
        """
        return self.execute_query(query, fetch=True)

    def get_all_parameters(self) -> List[Dict]:
        query = """
        SELECT p.*, e.model_name 
        FROM parameters p 
        LEFT JOIN experiments e ON p.experiment_id = e.id 
        ORDER BY p.id
        """
        return self.execute_query(query, fetch=True)


"""создаем глобальный экземпляр для использования во всем приложении"""
db = DatabaseManager()