import datetime

from airflow_assessment.utils import last_day_of_month


def test_last_day_of_month():
    # Test for a regular month
    date1 = datetime.datetime(2022, 1, 15)
    assert last_day_of_month(date1) == datetime.datetime(2022, 1, 31, 23, 59, 59, 999999)

    # Test for a leap year
    date2 = datetime.datetime(2020, 2, 20)
    assert last_day_of_month(date2) == datetime.datetime(2020, 2, 29, 23, 59, 59, 999999)

    # Test for December
    date3 = datetime.datetime(2023, 12, 10)
    assert last_day_of_month(date3) == datetime.datetime(2023, 12, 31, 23, 59, 59, 999999)
