from typing import Annotated, Optional
from datetime import date
from pydantic import BeforeValidator


def parse_date(v):
    if v is None or isinstance(v, date):
        return v
    if isinstance(v, str):
        return date.fromisoformat(v)
    return v


OptionalDate = Annotated[Optional[date], BeforeValidator(parse_date)]
