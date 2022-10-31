# Import external libraries
from fastapi.testclient import TestClient

# Import internal libraries
from app import app

# Test client
client = TestClient(app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == 'Welcome to the Nordea Project API!'


def test_ping():
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'pong'
    }


def test_get_cut_off():
    response = client.get('/getCutOff?currency_a=EUR&currency_b=USD&date=2022-10-31')
    assert response.status_code == 200
    assert response.json() == {
        'currency_a': {
            'iso': 'EUR',
            'country': 'Euro Area'
        },
        'currency_b': {
            'iso': 'USD',
            'country': 'United States'
        },
        'cut_off_time': '16.00'
    }


def test_get_cut_off_bad_currency():
    response = client.get('/getCutOff?currency_a=EURA&currency_b=USD&date=2022-10-31')
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': [
                    'query',
                    'currency_a'
                ],
                'msg': 'ensure this value has at most 3 characters',
                'type': 'value_error.any_str.max_length',
                'ctx': {
                    'limit_value': 3
                }
            }
        ]
    }


def test_get_cut_off_missing_currency():
    response = client.get('/getCutOff?currency_a=EUR&date=2022-10-31')
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': [
                    'query',
                    'currency_b'
                ],
                'msg': 'field required',
                'type': 'value_error.missing'
            }
        ]
    }


def test_get_cut_off_not_found_currency():
    response = client.get('/getCutOff?currency_a=AAA&currency_b=USD&date=2022-10-31')
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Currency A (AAA) not found.'
    }


def test_get_cut_off_bad_date():
    response = client.get('/getCutOff?currency_a=EUR&currency_b=USD&date=31/10/2022')
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': [
                    'query',
                    'date'
                ],
                'msg': 'invalid date format',
                'type': 'value_error.date'
            }
        ]
    }


def test_get_cut_off_missing_date():
    response = client.get('/getCutOff?currency_a=EUR&currency_b=USD')
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': [
                    'query',
                    'date'
                ],
                'msg': 'field required',
                'type': 'value_error.missing'
            }
        ]
    }


def test_get_cut_off_invalid_date():
    response = client.get('/getCutOff?currency_a=EUR&currency_b=USD&date=2022-01-01')
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'Invalid date: (2022-01-01) is in the past.'
    }
