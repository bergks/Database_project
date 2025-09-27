import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from config import DB_CONFIG
import logging
import sys

# Настраиваем логгер
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('DDOs_attacks_app')


class DatabaseManager:
    def __init__(self):
        self.connection_params = DB_CONFIG.copy()
        self.connection_params['client_encoding'] = 'UTF8'

    def get_connection(self, dbname=None, autocommit=False):
        """Устанавливает соединение с базой данных"""
        params = self.connection_params.copy()
        if dbname:
            params['dbname'] = dbname

        try:
            conn = psycopg2.connect(**params)
            if autocommit:
                conn.autocommit = True
            return conn
        except Exception as e:
            logger.error(f'Connection error: {str(e).encode("utf-8", errors="replace").decode("utf-8")}')
            raise

    def init_db(self):
        """Инициализация базы данных"""
        logger.info('Initializing database...')

        try:
            self._ensure_database_exists()
            self._ensure_tables_exist()

            logger.info('Database initialization completed successfully')

        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            logger.error(f'Error during database initialization: {error_msg}')
            raise

    def _ensure_database_exists(self):
        """Проверяет и создает базу данных если нужно"""
        conn_params = {
            'host': self.connection_params['host'],
            'user': self.connection_params['user'],
            'password': self.connection_params['password'],
            'dbname': 'postgres',
            'client_encoding': 'UTF8'
        }

        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                    ('ddosattacksdb',)
                )
                exists = cursor.fetchone() is not None
                logger.info(f'Database exists: {exists}')

                if not exists:
                    cursor.execute("CREATE DATABASE ddosattacksdb")
                    logger.info('Database created successfully')

        finally:
            conn.close()

    def _ensure_tables_exist(self):
        """Создает таблицы если они не существуют"""
        conn_params = {
            'host': self.connection_params['host'],
            'user': self.connection_params['user'],
            'password': self.connection_params['password'],
            'dbname': 'ddosattacksdb',
            'client_encoding': 'UTF8'
        }

        conn = psycopg2.connect(**conn_params)

        try:
            with conn.cursor() as cursor:
                self._create_tables(cursor)
                conn.commit()
                logger.info('Tables created/verified successfully')

        except Exception as e:
            conn.rollback()
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            logger.error(f'Table creation error: {error_msg}')
            raise
        finally:
            conn.close()

        # Обновляем параметры для будущих подключений
        self.connection_params['dbname'] = 'ddosattacksdb'

    def _create_tables(self, cursor):
        """Создает необходимые таблицы в базе данных"""
        try:
            cursor.execute("SELECT 1 FROM pg_type WHERE typname = 'experiment_status'")
            if not cursor.fetchone():
                cursor.execute("CREATE TYPE experiment_status as ENUM('active', 'completed','failed')")
                logger.info('Enum type created successfully')
            else:
                logger.info('Enum type already exists')
        except Exception as e:
            logger.warning(f'Enum type creation warning: {str(e)}')

        tables = [
            """
            CREATE TABLE IF NOT EXISTS experiments (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR NOT NULL,
                model_version VARCHAR NOT NULL,
                dataset_name VARCHAR NOT NULL,
                test_date DATE NOT NULL,
                experiment_status_enum experiment_status NOT NULL DEFAULT 'active',
                description TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attack_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS parameters (
                id SERIAL PRIMARY KEY,
                experiment_id INTEGER NOT NULL,
                parameter_name VARCHAR NOT NULL,
                parameter_value VARCHAR NOT NULL,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS experiment_metrics (
                id BIGSERIAL PRIMARY KEY,
                experiment_id INTEGER NOT NULL,
                attack_id INTEGER NOT NULL,
                accuracy FLOAT NOT NULL CHECK(accuracy BETWEEN 0 AND 1),
                precision FLOAT NOT NULL CHECK(precision BETWEEN 0 AND 1),
                recall FLOAT NOT NULL CHECK(recall BETWEEN 0 AND 1),
                FOREIGN KEY (experiment_id) REFERENCES experiments(id),
                FOREIGN KEY (attack_id) REFERENCES attack_types(id)
            )
            """
        ]

        for i, table_query in enumerate(tables):
            try:
                cursor.execute(table_query)
                logger.debug(f'Table {i + 1} created successfully')
            except Exception as e:
                logger.error(f'Error creating table {i + 1}: {str(e)}')
                continue

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Выполняет запрос к базе данных"""
        conn_params = self.connection_params.copy()
        conn_params['dbname'] = 'ddosattacksdb'
        conn_params['client_encoding'] = 'UTF8'

        conn = psycopg2.connect(**conn_params)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    result = cursor.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            logger.error(f'Query error: {error_msg}')
            raise
        finally:
            conn.close()

    def insert_experiment(self, model_name: str, model_version: str, dataset_name: str,
                          test_date: str, experiment_status_enum: str, description: str) -> int:
        """Добавляет эксперимент и возвращает его ID"""
        query = """
        INSERT INTO experiments (model_name, model_version, dataset_name, test_date, experiment_status_enum, description)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """
        try:
            result = self.execute_query(query, (model_name, model_version, dataset_name, test_date, experiment_status_enum,  description),
                                        fetch=True)
            if result and len(result) > 0:
                return result[0]['id']
            else:
                raise Exception("Failed to get experiment ID")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            logger.error(f"Insert experiment error: {error_msg}")
            raise

    def get_all_experiments(self) -> List[Dict]:
        """Получает все эксперименты"""
        query = "SELECT * FROM experiments ORDER BY id ASC"
        return self.execute_query(query, fetch=True)

    def get_experiment_by_id(self, experiment_id: int) -> Optional[Dict]:
        """Получает эксперимент по ID"""
        query = "SELECT * FROM experiments WHERE id = %s"
        result = self.execute_query(query, (experiment_id,), fetch=True)
        return result[0] if result else None

    def get_all_attack_types(self) -> List[Dict]:
        """Получает все типы атак"""
        query = "SELECT * FROM attack_types ORDER BY id"
        return self.execute_query(query, fetch=True)

    def insert_attack_type(self, name: str) -> int:
        """Добавляет новый тип атаки"""
        query = "INSERT INTO attack_types (name) VALUES (%s) RETURNING id"
        result = self.execute_query(query, (name,), fetch=True)
        return result[0]['id']

    def insert_parameter(self, experiment_id: int, parameter_name: str, parameter_value: str):
        """Добавляет параметр эксперимента"""
        query = """
        INSERT INTO parameters (experiment_id, parameter_name, parameter_value)
        VALUES (%s, %s, %s)
        """
        self.execute_query(query, (experiment_id, parameter_name, str(parameter_value)))

    def get_parameters_by_experiment(self, experiment_id: int) -> List[Dict]:
        """Получает параметры эксперимента"""
        query = "SELECT * FROM parameters WHERE experiment_id = %s"
        return self.execute_query(query, (experiment_id,), fetch=True)

    def insert_metric(self, experiment_id: int, attack_id: int, accuracy: float,
                      precision: float, recall: float):
        """Добавляет метрику эксперимента"""
        query = """
        INSERT INTO experiment_metrics (experiment_id, attack_id, accuracy, precision, recall)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_query(query, (experiment_id, attack_id, accuracy, precision, recall))

    def get_metrics_by_experiment(self, experiment_id: int) -> List[Dict]:
        """Получает метрики эксперимента"""
        query = """
        SELECT em.*, at.name as attack_name 
        FROM experiment_metrics em 
        LEFT JOIN attack_types at ON em.attack_id = at.id 
        WHERE em.experiment_id = %s
        """
        return self.execute_query(query, (experiment_id,), fetch=True)

    def get_all_metrics(self) -> List[Dict]:
        """Получает все метрики"""
        query = """
        SELECT em.*, e.model_name, at.name as attack_name 
        FROM experiment_metrics em 
        LEFT JOIN experiments e ON em.experiment_id = e.id 
        LEFT JOIN attack_types at ON em.attack_id = at.id 
        ORDER BY em.id
        """
        return self.execute_query(query, fetch=True)

    def get_all_parameters(self) -> List[Dict]:
        """Получает все параметры"""
        query = """
        SELECT p.*, e.model_name 
        FROM parameters p 
        LEFT JOIN experiments e ON p.experiment_id = e.id 
        ORDER BY p.id
        """
        return self.execute_query(query, fetch=True)


# Создаем глобальный экземпляр
db = DatabaseManager()

# Инициализируем базу данных
if __name__ == "__main__":
    try:
        db.init_db()
        print("Database initialized successfully!")
    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        print(f"Database initialization failed: {error_msg}")