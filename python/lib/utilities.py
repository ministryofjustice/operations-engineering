import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


def convert_str_to_bool(the_string: str) -> bool:
    if the_string in {"True", "true"}:
        return True
    return False


def get_username(user: dict[str, any]) -> str:
    return user["username"]


def convert_string_to_date(the_string: str) -> datetime:
    return datetime.strptime(the_string[0:10], '%Y-%m-%d')


def convert_timestamp_ms_to_date(timestamp_ms: int) -> datetime:
    return datetime.fromtimestamp(timestamp_ms / 1000.0)


def get_future_date(date_days: int, date_months: int, date_years: int) -> datetime:
    return datetime.now() + relativedelta(
        days=date_days, months=date_months, years=date_years
    )


def get_past_date(date_days: int, date_months: int, date_years: int) -> datetime:
    return datetime.now() - relativedelta(
        days=date_days, months=date_months, years=date_years
    )


def get_debug_mode() -> bool:
    debug_mode = os.getenv("DEBUG_MODE", "false")
    if isinstance(debug_mode, str):
        debug_mode = convert_str_to_bool(debug_mode)
    return debug_mode
