from datetime import datetime

from airflow.decorators import dag
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow_assessment.constant import POSTGRES_CON_ID

default_args = {
    "owner": "airflow-assessment",
    "start_date": datetime(2024, 1, 1),
}


@dag(schedule="@once", default_args=default_args, tags=["SQL"])
def create_views():
    create_view_transaction_enriched = PostgresOperator(
        task_id="create_view_transaction_enriched",
        postgres_conn_id=POSTGRES_CON_ID,
        sql="""
            CREATE OR REPLACE VIEW "transaction_enriched" AS 
            select 
                t.*, 
                t.amount * r.eur_rate as eur_amount, 
                SUBSTRING(t.payer, 0, 3) as "country_payer", 
                SUBSTRING(t.receiver, 0, 3) as "country_receiver"
            from transaction t
            join rate r on t.currency = r.currency;
            """,
    )

    create_view_balances = PostgresOperator(
        task_id="create_view_balances",
        postgres_conn_id=POSTGRES_CON_ID,
        sql="""
            CREATE OR REPLACE VIEW "account_balance" as
            select c.name, b.*
            from (
                select account, sum(mutation)
                from (
                    select payer as account, -eur_amount as "mutation"
                from transaction_enriched te
                UNION 
                select receiver as account, eur_amount as "mutation"
                from transaction_enriched)
                group by account
                ) as b
            join company c on c.iban = b.account;
            """,
    )

    create_view_transaction_enriched = PostgresOperator(
        task_id="create_view_transaction_enriched",
        postgres_conn_id=POSTGRES_CON_ID,
        sql="""
            CREATE OR REPLACE VIEW "interacted_countries" as
            select distinct account, interaction_country
            from (
                select payer as account, country_receiver as interaction_country
                from transaction_enriched
                union
                select receiver as account, country_payer as interaction_country
                from transaction_enriched
            )
            ORDER BY account
        """,
    )

    [create_view_transaction_enriched, create_view_balances]


@dag(schedule="@once", default_args=default_args, tags=["SQL"])
def drop_views():
    drop_view_transaction_enriched = PostgresOperator(
        task_id="drop_view_transaction_enriched",
        postgres_conn_id=POSTGRES_CON_ID,
        sql="DROP VIEW IF EXISTS transaction_enriched;",
    )

    drop_view_balances = PostgresOperator(
        task_id="drop_view_balances",
        postgres_conn_id=POSTGRES_CON_ID,
        sql="DROP VIEW IF EXISTS account_balance;",
    )

    drop_view_interacted_countries = PostgresOperator(
        task_id="drop_view_interacted_countries",
        postgres_conn_id=POSTGRES_CON_ID,
        sql="DROP VIEW IF EXISTS interacted_countries;",
    )

    [drop_view_transaction_enriched, drop_view_balances, drop_view_interacted_countries]
