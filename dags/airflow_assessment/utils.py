import datetime


def last_day_of_month(any_day: datetime.datetime) -> datetime.datetime:
    """
    Returns the last day of the month for a given date.

    Parameters:
        any_day (datetime.datetime): The date for which the last day of the month is to be determined.

    Returns:
        datetime.datetime: The last day of the month.

    """
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    last_day = next_month - datetime.timedelta(days=next_month.day)
    last_day = last_day.replace(hour=23, minute=59, second=59, microsecond=999999)
    return last_day
