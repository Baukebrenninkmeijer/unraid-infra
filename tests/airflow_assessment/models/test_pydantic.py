from datetime import datetime

from airflow_assessment.models.pydantic import (
    CompanyRaw,
    Rate,
    SepaTransaction,
    SwiftTransaction,
    Transaction,
)


def test_company_raw():
    company = CompanyRaw(address="123 Main St", ibans="NL12ABCD34567890", id=1, name="ACME Corp")
    assert company.address == "123 Main St"
    assert company.ibans == "NL12ABCD34567890"
    assert company.id == 1
    assert company.name == "ACME Corp"


def test_rate():
    rate = Rate(currency="USD", usd_rate=1.0, eur_rate=0.85)
    assert rate.currency == "USD"
    assert rate.usd_rate == 1.0
    assert rate.eur_rate == 0.85


def test_transaction():
    timestamp = datetime.now()
    transaction = Transaction(id="123456789", amount=100.0, currency="USD", timestamp=timestamp)
    assert transaction.id == "123456789"
    assert transaction.amount == 100.0
    assert transaction.currency == "USD"
    assert transaction.timestamp == timestamp


def test_sepa_transaction():
    timestamp = datetime.now()
    sepa_transaction = SepaTransaction(
        id="987654321", amount=200.0, currency="EUR", timestamp=timestamp, payer="John Doe", receiver="Jane Smith"
    )
    assert sepa_transaction.id == "987654321"
    assert sepa_transaction.amount == 200.0
    assert sepa_transaction.currency == "EUR"
    assert sepa_transaction.timestamp == timestamp
    assert sepa_transaction.payer == "John Doe"
    assert sepa_transaction.receiver == "Jane Smith"


def test_swift_transaction():
    timestamp = datetime.now()
    swift_transaction = SwiftTransaction(
        id="567890123", amount=300.0, currency="USD", timestamp=timestamp, sender="John Doe", beneficiary="Jane Smith"
    )
    assert swift_transaction.id == "567890123"
    assert swift_transaction.amount == 300.0
    assert swift_transaction.currency == "USD"
    assert swift_transaction.timestamp == timestamp
    assert swift_transaction.sender == "John Doe"
    assert swift_transaction.beneficiary == "Jane Smith"
