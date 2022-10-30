# Import external libraries
import datetime
from fastapi import FastAPI, Query, HTTPException

# Import internal libraries
from gateway_setup.gateway_middleware import MIDDLEWARE
from api_schemas.response_schemas import Pong, CutOffTime
from api_schemas.general_schemas import Currency
from db.db_manager import DB_Manager
from cut_off_times_utils import get_day_key, get_min_cut_off_time

# Simulating caching of queries
# As explained in the README, we store the cut-off times in memory to speed up response time.
# Read the README for me details and considerations.
cut_off_times_cache = DB_Manager.get_cache()

# API gateway
app = FastAPI(
    middleware=MIDDLEWARE,
    title='Nordea Project API',
    description='Nordea Coding Challenge API',
    version='0.0.1'
)


# Test APIs
@app.get('/', response_model=str)
async def root():
    return 'Welcome to the Nordea Project API!'


@app.get('/ping', response_model=Pong)
def ping() -> Pong:
    return Pong()


# Cut-off APIs
@app.get('/getCutOff', response_model=CutOffTime)
async def get_cut_off_time(
    # Here, we are very strict on the format of the input. For example, currency must be
    # 3 upper case letters. We could consider to lose it and handle different formats in our side.
    # For example, we could allow for lower case letters. It's a trade-off choice.
    currency_a: str = Query(min_length=3, max_length=3, regex='^[A-Z]+$'),
    currency_b: str = Query(min_length=3, max_length=3, regex='^[A-Z]+$'),
    date: datetime.date = Query()
) -> CutOffTime:
    # Since accessing a dict by key (only once) is an atomic operation, we do not need to use a lock.
    # Thus, even if we receive multiple request at the same time, they will be processed correctly.
    data_currency_a = cut_off_times_cache.get(currency_a, None)
    if data_currency_a is None:
        raise HTTPException(status_code=404, detail=f'Currency A ({currency_a}) not found.')
    data_currency_b = cut_off_times_cache.get(currency_b, None)
    if data_currency_b is None:
        raise HTTPException(status_code=404, detail=f'Currency B ({currency_b}) not found.')
    today = datetime.date.today()
    if date < today:
        raise HTTPException(status_code=422, detail=f'Invalid date: ({date}) is in the past.')

    day_key = get_day_key(date=date)
    return CutOffTime(
        currency_a=Currency(
            iso=currency_a,
            country=data_currency_a['country']
        ),
        currency_b=Currency(
            iso=currency_b,
            country=data_currency_b['country']
        ),
        cut_off_time=get_min_cut_off_time(cut_off_a=data_currency_a[day_key], cut_off_b=data_currency_b[day_key])
    )
