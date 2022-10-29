# Import external libraries
from pydantic import BaseModel


class Currency(BaseModel):
    iso: str
    country: str
