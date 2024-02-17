from datetime import datetime

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow_assessment.database import prep_database
from airflow_assessment.ingest import (
    ingest_companies,
    ingest_rates,
    retrieve_trades_single_day,
)


@dag(schedule="@monthly", start_date=datetime(2021, 1, 1), max_active_runs=6, tags=["cdn_ingestion"])
def create_summaries():
    prep_database_task = PythonOperator(
        task_id="prep_database",
        python_callable=prep_database,
    )

    ingest_companies_task = PythonOperator(
        task_id="ingest_companies",
        python_callable=ingest_companies,
        provide_context=True,
    )

    ingest_daily_trades_sepa_task = PythonOperator(
        task_id="ingest_daily_rates_sepa",
        python_callable=retrieve_trades_single_day,
        provide_context=True,
        op_kwargs={"url_suffix": "sepa"},
    )

    ingest_daily_trades_swift_task = PythonOperator(
        task_id="ingest_daily_rates_swift",
        python_callable=retrieve_trades_single_day,
        provide_context=True,
        op_kwargs={"url_suffix": "swift"},
    )

    ingest_rates_task = PythonOperator(
        task_id="ingest_rates",
        python_callable=ingest_rates,
    )

    prep_database_task >> [
        ingest_companies_task,
        ingest_daily_trades_sepa_task,
        ingest_daily_trades_swift_task,
        ingest_rates_task,
    ]


create_summaries()
