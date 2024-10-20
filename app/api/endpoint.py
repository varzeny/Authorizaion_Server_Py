# account/api.py

# lib
from fastapi import FastAPI, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

# module
from ..core.database import Manager as DB
from ..service.signup import Manager as SIGNUP
from ..service.access import Manager as ACCS


# define
router = APIRouter()
template = Jinja2Templates(directory="app/core/template")


# dependency
async def guest_only(req:Request):
    if req.state.access_token.get("role") == "guest":
        return req.state.access_token
    else:
        raise HTTPException(status_code=401, detail="you are not guest")

async def user_only(req:Request):
    if req.state.access_token.get("role") != "guest":
        return req.state.access_token
    else:
        raise HTTPException(status_code=401, detail="you are not user")
    
async def admin_only(req:Request):
    if req.state.access_token.get("role") == "admin":
        return req.state.access_token
    else:
        raise HTTPException(status_code=401, detail="you are not admin")


# endpoint
@router.get("/signup/page")
async def get_signup_page(req:Request, t=Depends(guest_only)):
    try:
        resp = template.TemplateResponse(
            request=req,
            name="signup.html",
            context={},
            status_code=200
        )

        resp.set_cookie(
            key=SIGNUP.token.key,
            value=SIGNUP.encoding_token( SIGNUP.token(seq="1").model_dump() ),
            max_age=SIGNUP.exp_main*60,
            secure=True,
            httponly=True
        )
        return resp
    
    except Exception as e:
        print("ERROR from get_signup_page : ", e)
        return Response(status_code=400)
    

@router.post("/signup/seq")
async def post_signup_seq(req:Request, ss:AsyncSession=Depends(DB.get_ss), t=Depends(guest_only)):
    try:
        encoded_token = req.cookies.get(SIGNUP.token.key)
        decoded_token = SIGNUP.decoding_token(encoded_token)
        reqData = await req.form()
        result = await SIGNUP.seq(decoded_token, reqData, ss)
        if not result:
            raise Exception("seq fail")
        
        resp = Response(status_code=200, content="seq"+result.get("seq"))
        resp.set_cookie(
            key=SIGNUP.token.key,
            value=SIGNUP.encoding_token( result ),
            max_age=SIGNUP.exp_main*60,
            secure=True,
            httponly=True
        )

    except Exception as e:
        print("ERROR from post_seq : ", e)
        resp = Response(status_code=400)

    finally:
        return resp


@router.get("/login/page")
async def get_login_page(req:Request, t=Depends(guest_only)):
    try:
        # referer
        referer = req.headers.get("referer")

        resp = template.TemplateResponse(
            request=req,
            name="login.html",
            context={"referer":referer},
            status_code=200
        )

    except Exception as e:
        print("ERROR from get_login_page : ", e)
        resp = Response(status_code=400)

    finally:
        return resp


@router.post("/login")
async def post_login(req:Request, ss:AsyncSession=Depends(DB.get_ss), t=Depends(guest_only)):
    try:
        # referer
        referer = req.headers.get("referer")

        # DB 확인
        reqData = await req.form()
        user = await ACCS.login(reqData.get("email"), reqData.get("pw"), ss)

        # 로그인 승인
        print("!!!!!",t)
        t["id"] = user.get("id")
        t["role"] = user.get("role")
        resp = Response(status_code=200)


    except Exception as e:
        print("ERROR from post_login_page : ", e)
        resp = Response(status_code=400, content=str(e))

    finally:
        return resp
    

@router.get("/logout")
async def get_logout(req:Request, t=Depends(user_only)):
    req.state.access_token={"role":"guest"}
    print(req.state.access_token)
    return Response(status_code=200)


@router.get("/check")
async def get_check(req:Request):
    return Response(status_code=200)