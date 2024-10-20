# service/access.py

# lib
from fastapi import FastAPI
from typing import ClassVar, Literal
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# module
from ..core.util import jwt
from ..core.util import hash

# define
class Token(BaseModel):
    key:ClassVar[str] = "access_token"
    role:Literal["admin", "user", "guest"] = Field(default="guest")
    id:int|None = Field(default=None)


class Manager:
    env:dict|None
    token = Token

    secret_key:str = None
    algorithm:str = None
    exp_min:int = None

    @classmethod
    def setup(cls, app:FastAPI):
        cls.env = app.state.env["app"]["service"]["access"]
        cls.secret_key = cls.env.get("secretkey")
        cls.algorithm = cls.env.get("algorithm")
        cls.exp_min = cls.env.get("expmin")

    @classmethod
    def encoding_token(cls, decoded_token:dict):
        encoded_token = jwt.create_jwt(
            payload=decoded_token,
            secret_key=cls.secret_key,
            algorithm=cls.algorithm,
            exp_min=cls.exp_min
        )
        return encoded_token

    @classmethod
    def decoding_token(cls, encoded_token:str):
        decoded_token = jwt.verify_jwt(
            encoded_token=encoded_token,
            secret_key=cls.secret_key,
            algorithm=cls.algorithm,
        )
        return decoded_token

    @classmethod
    async def login(cls, email:str, pw:str, ss:AsyncSession):
        resp = await ss.execute(
            statement=text(
                "SELECT * FROM account WHERE email=:email"
            ),
            params={"email":email}
        )
        respData = resp.mappings().fetchone()
        print(respData)

        if not respData:
            raise Exception("email doesn't exist")
        
        respData
        if not hash.verify_hash(pw, respData.get("pw_hashed")):
            raise Exception("pw doesn't match")
        
        return respData
    
    
