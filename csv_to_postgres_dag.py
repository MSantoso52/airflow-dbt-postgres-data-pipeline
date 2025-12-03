from airflow.decorators import dag
from datetime import datetime, timedelta
from airflow.providers.postgres.hook.postgres import PostgresHook
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import pandas as pd

FILE_PATH_1 = 'customer_data.csv'
FILE_PATH_2 = 'order.csv'
FILE_PATH_3 = 'order_item.csv'

db_config = {
    'host': 'localhost',
    'database': 'customers_db',
    'user': 'postgres',
    'password': 'duckdb'
}

table_1 = 'customers'
table_2 = 'orders'
table_3 = 'orderitems'

create_table_sql_1 = f'''
    CREATE TABLE IF NOT EXISTS customers(
        customer_id INTEGER PRIMARY KEY,
        full_name VARCHAR(255),
        address VARCHAR(255),
        city VARCHAR(255),
        zipcode INTEGER
    );
'''

create_table_sql_2 = f'''
    CREATE TABLE IF NOT EXISTS orders(
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE,
        product_name VARCHAR(255),
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        total_price DECIMAL(10,2)
    );
'''

create_table_sql_3 = f'''
    CREATE TABLE IF NOT EXISTS orderitems(
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        item_name VARCHAR(255),
        item_quantity INTEGER,
        item_unit_price DECIMAL(10,2),
        item_total_price DECIMAL(10,2)
    );
'''

sql_insert_1 = f'''
    INSERT INTO customers (customer_id, full_name, address, city, zipcode)
    VALUES (%s, %s, %s, %s, %s)
'''

sql_insert_2 = f'''
    INSERT INTO orders (order_id, customer_id, order_date, product_name, quantity, unit_price, total_price)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
'''

sql_insert_3 = f'''
    INSERT INTO orderitems (order_item_id, order_id, item_name, item_quantity, item_unit_price, item_total_price)
    VALUES (%s, %s, %s, %s, %s, %s)
'''

DBT_PROJECT_DIR = '/home/mulyo/dbt_snowflake/customers'
DBT_PROFILE = 'customers'

# --- Python function to ingest CSV ---
def data_ingestion(
        file_path: str,
        psql_connection: str,
        create_table_sql: str,
        sql_insert: str,
        **kwarg
)-> None:
    # 1. Read CSV using pandas
    df = pd.read_csv(file_path)
        
    # 2. Get connection from PostgresHook & load the datas
    try:
        hook = PostgresHook(psql_connection)
        with hook.get_conn as conn:
            with conn.cursor as cursor:
                cursor.execute(create_table_sql)
                conn.commit()

                for index, row in df.iterrow():
                    cursor.execute(sql_insert, row.to_list())
                conn.commit()
    except Exception as e:
        print(e)


POSTGRES_CONN_ID = 'postgres_conn'

default_arg = {
    'owner': 'mulyo',
    'tries': 5,
    'try_delay': timedelta(minutes=2)
}

@dag(
    dag_id = 'csv_to_postgres',
    description = 'data ingestion and transformation on postgres',
    default_arg = default_arg,
    start_date = datetime(2025, 12, 3),
    schedule = None,
    catchup = False,
    tags = ['csv', 'postgres', 'dbt']
)
def csv_to_postgres():
        
    load_customer_data = PythonOperator(
        task_id = 'load_customer_data',
        python_callable = data_ingestion,
        op_kwarg = {
            'file_path': FILE_PATH_1,
            'psql_connection': POSTGRES_CONN_ID,
            'create_table_sql': create_table_sql_1,
            'sql_insert': sql_insert_1
        },
    ) 

    load_orders = PythonOperator(
        task_id = 'load_orders',
        python_callable = data_ingestion,
        op_kwarg = {
            'file_path': FILE_PATH_2,
            'psql_connection': POSTGRES_CONN_ID,
            'create_table_sql': create_table_sql_2,
            'sql_insert': sql_insert_2
        },
    )

    load_order_items = PythonOperator(
        task_id = 'load_order_items',
        python_callable = data_ingestion,
        op_kwarg = {
            'file_path': FILE_PATH_3,
            'psql_connection': POSTGRES_CONN_ID,
            'create_table_sql': create_table_sql_3,
            'sql_insert': sql_insert_3
        },
    )

    run_dbt_model = BashOperator(
        task_id = 'run_dbt_model',
        bash_command = f'''
            cd {DBT_PROJECT_DIR} && dbt run --profile {DBT_PROFILE}
        ''',
    )

    [load_customer_data, load_orders, load_order_items] >> run_dbt_model

csv_to_postgres()
