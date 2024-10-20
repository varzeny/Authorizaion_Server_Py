# access_mw.py

# lib
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from fastapi.responses import Response

# module
from ..service.access import Manager as ACCS

# define
class MW(BaseHTTPMiddleware):
    async def dispatch(self, req:Request, call_next):
        # 전처리
        encoded_token = req.cookies.get("access_token")

        if encoded_token:
            decoded_token = ACCS.decoding_token(encoded_token)
            if decoded_token:
                print("토큰 있음", decoded_token)
            else:
                print("")

        else:
            decoded_token = {"role":"guest", "id":None}
            print("토큰 없어서 만듬", decoded_token)

        req.state.access_token = decoded_token
        
        # 엔드포인트로 넘김 ###############################################
        resp:Response = await call_next(req)

        # 후처리
        resp.set_cookie(
            key=ACCS.token.key,
            value=ACCS.encoding_token(req.state.access_token),
            max_age=ACCS.exp_min*60,
            secure=True,
            httponly=True
        )

        return resp
