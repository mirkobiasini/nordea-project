# Import external libraries
import datetime
from pydantic import BaseModel

# Import internal libraries
from api_schemas.general_schemas import Currency


class Pong(BaseModel):
    message: str = 'pong'


class CutOffTime(BaseModel):
    currency_a: Currency
    currency_b: Currency
    cut_off_time: str
