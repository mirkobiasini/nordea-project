# Import external libraries
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# TODO explain that this is not safe just for the example
_origins = [
    "*"
]

MIDDLEWARE = [
    Middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]
