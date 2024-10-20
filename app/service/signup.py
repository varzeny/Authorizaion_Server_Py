# account/service/signup.py

# lib
from fastapi import FastAPI
from typing import ClassVar
from pydantic import BaseModel, Field
from random import randint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# module
from app.core.util import jwt, email, hash

# define
class Token(BaseModel):
    key:ClassVar[str] = "signup_token"
    seq:str|None = Field(default=None)
    email: str | None = Field(default=None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    code:int|None = Field(default=None)


class Manager:
    env:dict|None
    token = Token

    secret_key:str = None
    algorithm:str = None
    exp_main:int = None

    smtp_host:str|None
    smtp_port:int|None
    sender_id:str|None
    sender_pw:str|None

    @classmethod
    def setup(cls, app:FastAPI):
        cls.env = app.state.env["app"]["service"]["signup"]
        cls.secret_key = cls.env.get("secretkey")
        cls.algorithm = cls.env.get("algorithm")
        cls.exp_main = cls.env.get("expmin")

        cls.smtp_host = cls.env.get("smtphost")
        cls.smtp_port = cls.env.get("smtpport")
        cls.sender_id = cls.env.get("senderid")
        cls.sender_pw = cls.env.get("senderpw")


    @classmethod
    def encoding_token(cls, decoded_token:dict):
        encoded_token = jwt.create_jwt(
            payload=decoded_token,
            secret_key=cls.secret_key,
            algorithm=cls.algorithm,
            exp_min=cls.exp_main
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
    async def seq(cls, decoded_token:dict, reqData, ss:AsyncSession):
        try:
            if not decoded_token.get("seq") == reqData.get("seq"):
                raise Exception("토큰과 요청의 seq 가 다름")
            
            seq = decoded_token.get("seq")

            # email
            if seq == "1":
                email_addr = reqData.get("email")
                print(email_addr)
                
                resp = await ss.execute(
                    statement=text("SELECT id FROM account WHERE email=:email;"),
                    params={"email":email_addr}
                )

                respData = resp.fetchall()

                if respData:
                    raise Exception("이미 등록된 이메일")

                code = str( randint(10000, 99999) )

                if not await email.send_email(
                    smtp_host=cls.smtp_host,
                    smtp_port=cls.smtp_port,
                    sender_addr=cls.sender_id,
                    sender_pw=cls.sender_pw,
                    receiver_addr=email_addr,
                    subject="Your verify code has arrived.",
                    bodyData=code
                ):
                    raise Exception("이메일 전송 오류")

                decoded_token["email"] = email_addr
                decoded_token["code"] = code
                decoded_token["seq"] = "2"
                return decoded_token
            
            # code
            elif seq == "2":
                if not decoded_token.get("code") == reqData.get("code"):
                    raise Exception("토큰과 요청의 code 가 다름")
                decoded_token["seq"] = "3"
                return decoded_token
                
            # pw
            elif seq == "3":
                token = cls.token(**decoded_token)

                resp = await ss.execute(
                    statement=text("INSERT INTO account(role, email, pw_hashed) values(:role, :email, :pw_hashed);"),
                    params={
                        "role":"user",
                        "email":token.email,
                        "pw_hashed":hash.create_hash(reqData.get("pw"))
                    }
                )
                await ss.commit()
                decoded_token["seq"] = "4"
                return decoded_token
            
            else:
                raise Exception("등록되지 않은 seq")
        
        except Exception as e:
            print( "ERROR from seq : ", e)
            return None

