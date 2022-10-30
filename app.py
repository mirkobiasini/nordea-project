# Import external libraries
import datetime
from fastapi import FastAPI, Query, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import internal libraries
from gateway_setup.gateway_middleware import MIDDLEWARE
from api_schemas.response_schemas import Pong, CutOffTime
from api_schemas.general_schemas import Currency
from db.db_manager import DB_Manager
from cut_off_times_utils import get_day_key, get_min_cut_off_time

# Simulating caching of queries
# TODO Explain properly the approach
cut_off_times_cache = DB_Manager.get_cache()

# API gateway
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    middleware=MIDDLEWARE,
    title='Nordea Project API',
    description='Nordea Coding Challenge API',
    version='0.0.1'
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Test APIs
@app.get('/', response_model=str)
# @limiter.limit('5/minute')
async def root():
    return 'Welcome to the Nordea Project API!'


@app.get('/ping', response_model=Pong)
# @limiter.limit('5/minute')
def ping() -> Pong:
    return Pong()


# Cut-off APIs
@app.get('/getCutOff', response_model=CutOffTime)
# @limiter.limit('5/minute')
async def get_cut_off_time(
    # TODO Explain that we could ne less strict, e.g. allow lower case.
    currency_a: str = Query(min_length=3, max_length=3, regex='^[A-Z]+$'),
    currency_b: str = Query(min_length=3, max_length=3, regex='^[A-Z]+$'),
    date: datetime.date = Query()
) -> CutOffTime:
    # TODO Getting keys is atomic, so no lock
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


if __name__ == '__main__':
    print('Nordea Coding Challenge by Mirko Biasini')
