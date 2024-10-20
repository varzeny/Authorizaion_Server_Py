# app/__init__.py

# lib
from fastapi import FastAPI

# module
from .middleware.check import MW as ACCS_MW
from .core.database import Manager as DB
from .service.signup import Manager as SIGNUP
from .service.access import Manager as ACCS
from .api.endpoint import router as API

# define
class Manager:
    env:dict|None
    middleware = ACCS_MW

    @classmethod
    def setup(cls, app:FastAPI):
        # env
        cls.env = app.state.env
        
        # db
        DB.setup(app)

        # service
        SIGNUP.setup(app)
        ACCS.setup(app)

        # endpoint
        app.include_router( API )
