import logging
from datetime import datetime
from typing import Any, Type

import pandas as pd
import pytz
import requests
from airflow_assessment.constant import CDM_API_URL, POSTGRES_CON_ID
from airflow_assessment.database import (
    delete_rows_from_interval,
    get_engine_from_airflow_conn_id,
    truncate_table,
    write_to_database,
)
from airflow_assessment.models.alchemy import CompanyModel, RateModel, TransactionModel
from airflow_assessment.models.pydantic import (
    CompanyRaw,
    Rate,
    SepaTransaction,
    SwiftTransaction,
    Transaction,
)
from airflow_assessment.transformations import transform_companies, transform_trades
from airflow_assessment.utils import last_day_of_month
from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)
TIMESTAMP_COL = "timestamp"


def get_json_from_url(url: str, params: Any | None = None) -> list[dict]:
    """
    Retrieves JSON data from the specified URL.

    Args:
        url (str): The URL to retrieve JSON data from.
        params (Any | None, optional): Additional parameters for the request. Defaults to None.

    Returns:
        list[dict]: The JSON data as a list of dictionaries.
    """
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(f"Failed to get json from url: {res.status_code=}, {res.text=}")
    except Exception as e:
        raise Exception(f"Failed to get json from url: {e=}")


def get_companies_from_api(url: str = CDM_API_URL) -> pd.DataFrame:
    """
    Retrieves companies data from the API.

    Args:
        url (str, optional): The URL of the API. Defaults to CDM_API_URL.

    Returns:
        pd.DataFrame: The companies data as a pandas DataFrame.
    """
    results = get_json_from_url(url=f"{url}/companies")
    validate_data(data=results, model=CompanyRaw)
    LOGGER.debug("Successfully validated all companies data")
    companies = pd.DataFrame(results)
    companies = transform_companies(companies)
    return companies


def validate_data(data: list[dict], model: Type[BaseModel]):
    """
    Validates the given data against the specified Pydantic model.

    Args:
        data (list[dict]): The data to validate.
        model (Type[BaseModel]): The Pydantic model to validate against.
    """
    for item in data:
        try:
            model.model_validate(item)
        except Exception as e:
            LOGGER.warning(f"Failed to validate data: {e=} --- {item=}")


def retrieve_rates_from_api(url: str = CDM_API_URL):
    """
    Retrieves exchange rates data from the API.

    Args:
        url (str, optional): The URL of the API. Defaults to CDM_API_URL.

    Returns:
        pd.DataFrame: The exchange rates data as a pandas DataFrame.
    """
    results = get_json_from_url(url=f"{url}/exchange-rates")
    validate_data(data=results, model=Rate)
    return pd.DataFrame(results)


def ingest_companies(*args, **kwargs):
    """
    Ingests companies data into the database.
    """
    engine = get_engine_from_airflow_conn_id(conn_id=POSTGRES_CON_ID)

    LOGGER.info("Retrieving companies from api")
    companies = get_companies_from_api()
    LOGGER.info(f"Retrieving {len(companies)} from api.")
    if companies.empty:
        LOGGER.info("Companies data is empty. Not writing to database.")
        return

    truncate_table(engine=engine, model=CompanyModel)
    write_to_database(engine=engine, data=companies, model=CompanyModel, if_exists="append")


def ingest_rates(*args, **kwargs):
    """
    Ingests exchange rates data into the database.
    """
    engine = get_engine_from_airflow_conn_id(conn_id=POSTGRES_CON_ID)

    rates = retrieve_rates_from_api(url=CDM_API_URL)
    LOGGER.info(f"Succesfully retrieved {len(rates)} exchange rates from API.")
    if rates.empty:
        LOGGER.info(f"Trade data is empty. Not writing to database. {engine}")
        return

    truncate_table(engine=engine, model=RateModel)
    write_to_database(engine=engine, data=rates, model=RateModel, if_exists="append")


def retrieve_trades_single_day(url_suffix: str, *args, **kwargs):
    """
    Retrieves trades data for a single day from the API.

    Args:
        url_suffix (str): The URL suffix for the specific type of trades.
    """
    execution_date = str(kwargs["ts"])
    execution_date = datetime.strptime(execution_date, "%Y-%m-%dT%H:%M:%S%z")
    engine = get_engine_from_airflow_conn_id(conn_id=POSTGRES_CON_ID)

    end_ts = last_day_of_month(execution_date)

    delete_rows_from_interval(
        engine=engine, model=TransactionModel, start_date=execution_date, end_date=end_ts, timestamp_col=TIMESTAMP_COL
    )

    validation_model = SepaTransaction if url_suffix == "sepa" else SwiftTransaction

    trades = get_transactions_from_api_interval(
        start_date=execution_date,
        end_ts=end_ts,
        url=f"{CDM_API_URL}/transactions/{url_suffix}",
        validation_model=validation_model,
    )
    if trades.empty:
        LOGGER.info(f"Trade data is empty. Not writing to database. {engine}")
        return
    trades = transform_trades(trades)
    LOGGER.info(f"Writing trade data to database {engine}")
    write_to_database(engine=engine, data=trades, model=TransactionModel, if_exists="append")


def get_transactions_from_api_interval(
    start_date: datetime, end_ts: datetime, url: str, validation_model: Type[Transaction]
) -> pd.DataFrame:
    """
    Retrieves trades data for a specific interval from the API.

    Args:
        start_date (datetime): The start date of the interval.
        end_ts (datetime): The end date of the interval.
        url (str): The URL of the API.
        validation_model (Type[Transaction]): The Pydantic model to validate against.

    Returns:
        pd.DataFrame: The trades data as a pandas DataFrame.
    """
    LOGGER.info(f"Retrieving SEPA transactions from API for {start_date}")
    data = []
    cur_ts = start_date
    ts_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    payload = {
        "limit": 5000,
        "after-timestamp": start_date.strftime(ts_format),
    }
    while cur_ts < end_ts:
        LOGGER.debug(f'{payload["after-timestamp"]}')
        payload_str = "&".join(f"{k}={v}" for k, v in payload.items())
        results = get_json_from_url(url=url, params=payload_str)
        validate_data(data=results, model=validation_model)
        if not results:
            break
        data.extend(results)
        payload["after-timestamp"] = results[-1][TIMESTAMP_COL]
        cur_ts = pytz.utc.localize(datetime.strptime(results[-1][TIMESTAMP_COL], ts_format))
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL])
    # Filter out transactions that are not from the interval
    df = df.loc[df[TIMESTAMP_COL] <= end_ts, :]
    return df
