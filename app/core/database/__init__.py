# database/__init__.py

# lib
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

# module


# define
class Manager:
    ENV:dict|None
    engine:AsyncEngine|None
    session:AsyncSession|None

    @classmethod
    def setup(cls, app:FastAPI):
        cls.ENV = app.state.env.get("app")
        cls.engine = create_async_engine( cls.ENV["core"]["database"]["url"] )
        cls.session = async_sessionmaker(
            bind=cls.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @classmethod
    async def get_ss(cls):
        try:
            ss:AsyncSession = cls.session()
            yield ss
        except Exception as e:
            print("ERROR from get_ss : ", e)
            await ss.rollback()
        finally:
            await ss.close()