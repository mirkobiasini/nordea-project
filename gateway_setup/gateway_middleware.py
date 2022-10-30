# Import external libraries
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Note, for simplicity, we are allowing all origins. This exposes our endpoint to possible attacks.
# In a real life case, depending on the requirements, we would implement an authorization system, CORS, etc.
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
