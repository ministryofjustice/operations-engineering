import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_past_date(date_days: int, date_months: int, date_years: int):
    return datetime.now() - relativedelta(
        days=date_days, months=date_months, years=date_years
    )
