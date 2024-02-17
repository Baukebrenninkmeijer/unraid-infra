from typing import Union

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Identity

prod_base = declarative_base()


class CompanyModel(prod_base):
    """
    Represents a company in the database.

    Attributes:
        iban (str): The IBAN of the company.
        company_id (int): The ID of the company.
        name (str): The name of the company.
        address (str): The address of the company.
        country (str): The country of the company.
    """

    __tablename__ = "company"

    iban = Column(String, primary_key=True)
    company_id = Column(Integer)
    name = Column(String)
    address = Column(String)
    country = Column(String)


class RateModel(prod_base):
    """
    Represents a currency rate in the database.

    Attributes:
        currency (str): The currency code.
        usd_rate (float): The rate against USD.
        eur_rate (float): The rate against EUR.
    """

    __tablename__ = "rate"

    currency = Column(String, primary_key=True)
    usd_rate = Column(Float)
    eur_rate = Column(Float)
    eur_rate = Column(Float)


class TransactionModel(prod_base):
    """
    Represents a transaction in the database.

    Attributes:
        id (int): The ID of the transaction.
        trade_id (str): The trade ID of the transaction.
        payer (str): The payer of the transaction.
        receiver (str): The receiver of the transaction.
        amount (float): The amount of the transaction.
        currency (str): The currency of the transaction.
        timestamp (datetime): The timestamp of the transaction.
    """

    __tablename__ = "transaction"

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    trade_id = Column(String)
    payer = Column(String)
    receiver = Column(String)
    amount = Column(Float)
    currency = Column(String)
    timestamp = Column(DateTime)


TableTypes = Union[CompanyModel, RateModel, TransactionModel]
