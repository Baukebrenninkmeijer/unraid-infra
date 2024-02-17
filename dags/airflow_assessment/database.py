import logging
from datetime import datetime
from typing import Literal

import pandas as pd
import sqlalchemy
from airflow.models import Connection
from airflow_assessment.constant import AIRFLOW_SCHEMA_NAME, POSTGRES_CON_ID
from airflow_assessment.models.alchemy import TableTypes, prod_base
from sqlalchemy import create_engine, delete, inspect
from sqlalchemy.engine import URL, Engine

LOGGER = logging.getLogger(__name__)


def get_connection_with_airflow_conn_id(conn_id: str) -> Connection:
    """
    Retrieves the database credentials for a given connection ID.

    Args:
        conn_id (str): The connection ID.

    Returns:
        Connection: The database connection details.
    """
    conn_details = Connection.get_connection_from_secrets(conn_id=conn_id)
    return conn_details


def get_database_url_from_connection(conn_details: Connection) -> URL:
    """
    Generates a database URL from the given connection details.

    Args:
        conn_details (Connection): The database connection details.
        schema (bool, optional): Whether to include the schema in the URL. Defaults to True.

    Returns:
        URL: The database URL.
    """
    return URL.create(
        drivername="postgresql+psycopg2",
        username=conn_details.login,
        password=conn_details.password,
        host=conn_details.host,
        port=conn_details.port,
        database=conn_details.schema,
    )


def create_table_if_not_exists(engine: Engine, model: TableTypes) -> None:
    """
    Creates a table if it does not already exist in the database.

    Args:
        engine (Engine): The database engine.
        model (TableTypes): The table model.

    Returns:
        None
    """
    if not table_exists(engine=engine, table_name=model.__tablename__, schema=model.__table_args__["schema"]):
        logging.info(f"Creating table: {model.__tablename__}")
        model.__table__.create(engine)
    else:
        logging.info(f"Table already exists: {model.__tablename__}")


def table_exists(engine: Engine, table_name: str, schema: str | None = None) -> bool:
    """
    Checks if a table exists in the database.

    Args:
        engine (Engine): The database engine.
        table_name (str): The name of the table.
        schema (str | None, optional): The schema of the table. Defaults to None.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    return inspect(engine).has_table(table_name, schema=schema)


def create_schema_if_not_exists_from_conn_id(conn_id: str, schema_name: str):
    """
    Creates a schema if it does not already exist in the database.

    Args:
        conn_id (str): The connection ID.
        schema_name (str): The name of the schema.

            Returns:
        None
    """
    engine = get_engine_from_airflow_conn_id(conn_id=conn_id)
    create_schema_if_not_exists_with_engine(engine=engine, schema_name=schema_name)


def create_schema_if_not_exists_with_engine(engine: Engine, schema_name: str):
    """
    Creates a schema using the given database engine.

    Args:
        engine (Engine): The database engine.
        schema_name (str): The name of the schema.

    Returns:
        None
    """
    if schema_name not in inspect(engine).get_schema_names():
        engine.execute(sqlalchemy.schema.CreateSchema(name=schema_name))


def get_engine_from_airflow_conn_id(conn_id: str) -> Engine:
    """
    Retrieves a database engine from the given connection ID.

    Args:
        conn_id (str): The connection ID.
        schema (bool, optional): Whether to include the schema in the engine. Defaults to True.

    Returns:
        Engine: The database engine.
    """
    db_credentials = get_connection_with_airflow_conn_id(conn_id=conn_id)
    db_url = get_database_url_from_connection(conn_details=db_credentials)
    engine = create_engine(url=db_url)
    return engine


def create_tables(engine: Engine):
    """
    Creates tables in the database using the given engine.

    Args:
        engine (Engine): The database engine.

    Returns:
        None
    """
    prod_base.metadata.create_all(engine)


def prep_database():
    """
    Prepares the database by creating tables and schemas.

    Returns:
        None
    """
    create_schema_if_not_exists_from_conn_id(conn_id="postgres-details", schema_name=AIRFLOW_SCHEMA_NAME)
    create_tables(engine=get_engine_from_airflow_conn_id(conn_id=POSTGRES_CON_ID))


def delete_rows_from_interval(
    engine: sqlalchemy.engine.Engine, model, start_date: datetime, end_date: datetime, timestamp_col: str
):
    from sqlalchemy.sql import column

    ts_col = column(timestamp_col)
    delete_stmt = delete(model).where(ts_col.between(start_date, end_date))

    stmt = str(delete_stmt.compile(engine))

    stmt = f"""
    DELETE FROM "{model.__table_args__['schema']}".{model.__tablename__}
    where {timestamp_col} between '{start_date}' and '{end_date}'
    """
    LOGGER.info(stmt)

    with engine.connect() as connection:
        result = connection.execute(stmt)
        LOGGER.info(f"{result.rowcount} rows deleted.")


def write_to_database(
    engine: Engine, model: TableTypes, data: pd.DataFrame, if_exists: Literal["replace", "append", "fail"] = "replace"
):
    """
    Writes the given DataFrame to the database using the given engine and table model.

    Args:
        engine (Engine): The database engine.
        model (TableTypes): The table model.
        data (pd.DataFrame): The DataFrame to write to the database.
        if_exists (str, optional): The behaviour if the table already exists. Defaults to "replace".

    Returns:
        None
    """
    data.to_sql(
        name=model.__tablename__,
        con=engine,
        if_exists=if_exists,
        schema=model.__table_args__["schema"],
        index=False,
    )
    LOGGER.info(f"Written {len(data)} rows to database {model.__tablename__=}.")


def truncate_table(engine: Engine, model: TableTypes):
    """
    Truncates the given table in the database.

    Args:
        engine (Engine): The database engine.
        model (TableTypes): The table model.

    Returns:
        None
    """
    with engine.connect() as connection:
        connection.execute(f"""TRUNCATE TABLE "{model.__table_args__['schema']}".{model.__tablename__}""")
        LOGGER.info(f"Truncated table: {model.__tablename__}")
