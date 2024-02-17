from datetime import datetime

from pydantic import BaseModel


class CompanyRaw(BaseModel):
    """
    Represents a raw company data.

    Attributes:
        address (str): The address of the company.
        ibans (str): The IBANs associated with the company.
        id (int): The ID of the company.
        name (str): The name of the company.
    """

    address: str
    ibans: str
    id: int
    name: str


class Rate(BaseModel):
    """
    Represents a currency rate.

    Attributes:
        currency (str): The currency code.
        usd_rate (float): The rate against USD.
        eur_rate (float): The rate against EUR.
    """

    currency: str
    usd_rate: float
    eur_rate: float


class Transaction(BaseModel):
    """
    Represents a transaction.

    Attributes:
        id (str): The ID of the transaction.
        amount (float): The amount of the transaction.
        currency (str | None): The currency of the transaction (optional).
        timestamp (datetime): The timestamp of the transaction.
    """

    id: str
    amount: float
    currency: str | None
    timestamp: datetime


class SepaTransaction(Transaction):
    """
    Represents a SEPA transaction.

    Attributes:
        payer (str): The payer of the transaction.
        receiver (str): The receiver of the transaction.
    """

    payer: str
    receiver: str


class SwiftTransaction(Transaction):
    """
    Represents a SWIFT transaction.

    Attributes:
        sender (str): The sender of the transaction.
        beneficiary (str): The beneficiary of the transaction.
    """

    sender: str
    beneficiary: str
