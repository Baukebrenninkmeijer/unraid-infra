import sys

import pytest
from airflow_assessment.models.alchemy import CompanyModel, RateModel, TransactionModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print(sys.path)


@pytest.fixture(scope="module")
def session():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")

    Session = sessionmaker(bind=engine)
    session = Session()

    CompanyModel.metadata.create_all(engine)
    RateModel.metadata.create_all(engine)
    TransactionModel.metadata.create_all(engine)
    yield session
    # Clean up the database after each test
    CompanyModel.metadata.drop_all(engine)
    RateModel.metadata.drop_all(engine)
    TransactionModel.metadata.drop_all(engine)
    session.close()


def test_company_model(session):
    # Test creating and querying a CompanyModel object
    company = CompanyModel(
        iban="NL123456789", company_id=1, name="Company A", address="123 Main St", country="Netherlands"
    )
    session.add(company)
    session.commit()

    queried_company = session.query(CompanyModel).filter_by(iban="NL123456789").first()
    assert queried_company.name == "Company A"


def test_rate_model(session):
    # Test creating and querying a RateModel object
    rate = RateModel(currency="USD", usd_rate=1.0, eur_rate=0.9)
    session.add(rate)
    session.commit()

    queried_rate = session.query(RateModel).filter_by(currency="USD").first()
    assert queried_rate.eur_rate == 0.9


def test_transaction_model(session):
    # Test creating and querying a TransactionModel object
    transaction = TransactionModel(
        trade_id="123456789", payer="Company A", receiver="Company B", amount=100.0, currency="USD"
    )
    session.add(transaction)
    session.commit()

    queried_transaction = session.query(TransactionModel).filter_by(trade_id="123456789").first()
    assert queried_transaction.amount == 100.0
    assert queried_transaction.amount == 100.0
    assert queried_transaction.amount == 100.0
    assert queried_transaction.amount == 100.0
