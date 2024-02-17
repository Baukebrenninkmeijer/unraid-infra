import pandas as pd


def transform_companies(companies: pd.DataFrame, iban_field_name: str = "ibans") -> pd.DataFrame:
    """
    Transforms the given DataFrame of companies.

    Args:
        companies (pd.DataFrame): The DataFrame of companies.

    Returns:
        pd.DataFrame: The transformed DataFrame of companies.
    """
    companies[iban_field_name] = companies[iban_field_name].apply(pd.eval)  # type: ignore
    companies = companies.explode(iban_field_name)
    companies["country"] = companies[iban_field_name].str.slice(0, 2)
    companies = companies.rename(columns={iban_field_name: "iban", "id": "company_id"})
    return companies


def transform_trades(trades: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the given DataFrame of trades.

    Args:
        trades (pd.DataFrame): The DataFrame of trades.

    Returns:
        pd.DataFrame: The transformed DataFrame of trades.
    """
    trades["timestamp"] = pd.to_datetime(trades["timestamp"])
    column_mapping = {"sender": "payer", "beneficiary": "receiver", "id": "trade_id"}
    trades = trades.rename(columns=column_mapping, errors="ignore")
    return trades
