# Import external libraries
import datetime
from fastapi import FastAPI, Depends, APIRouter, Query, Response, HTTPException, Body, Request

# Import internal libraries
from gateway_setup.gateway_middleware import MIDDLEWARE
from api_schemas.response_schemas import Pong, CutOffTime
from api_schemas.general_schemas import Currency

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
async def get_twitter_table_audits(
    # TODO Explain that we could ne less strict, e.g. allow lower case.
    currency_a: str = Query(min_length=3, max_length=3, regex='^[A-Z]+$'),
    currency_b: str = Query(min_length=3, max_length=3, regex='^[A-Z]+$'),
    date: datetime.date = Query()
) -> CutOffTime:
    # TODO Replace with check if currency exists in db
    if currency_a and False:
        raise HTTPException(status_code=404, detail=f'Currency {currency_a} not found.')
    if currency_b and False:
        raise HTTPException(status_code=404, detail=f'Currency {currency_b} not found.')

    return CutOffTime(
        currency_a=Currency(
            iso=currency_a,
            country='Test country A'
        ),
        currency_b=Currency(
            iso=currency_b,
            country='Test country B'
        ),
        cut_off_time=datetime.datetime.now()
    )


if __name__ == '__main__':
    print('Nordea Coding Challenge by Mirko Biasini')
