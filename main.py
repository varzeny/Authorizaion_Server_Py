# main.py

# lib
from os import getenv
from dotenv import load_dotenv
from fastapi import FastAPI, staticfiles

# module
from app import Manager as APP

# define
load_dotenv()


async def startup():
    print("-"*40, app.state.env.get("project")["name"], "-"*40)

    APP.setup(app)
    
    return

async def shutdown():
    print("-"*40, "end", "-"*40)
    return

app = FastAPI()
app.state.env = {
    "project":{
        "name":getenv("PROJECT_NAME"),
        "host":getenv("PROJECT_HOST"),
        "port":int(getenv("PROJECT_PORT")),
    },
    "app":{
        "core":{
            "database":{
                "url":getenv("APP_CORE_DATABASE_URL")
            },
        },
        "service":{
            "signup":{
                "secretkey":getenv("SERVICE_SIGNUP_SECRETKEY"),
                "algorithm":getenv("SERVICE_SIGNUP_ALGORITHM"),
                "expmin":int(getenv("SERVICE_SIGNUP_EXPMIN")),
                "smtphost":getenv("SERVICE_EMAIL_SMTPHOST"),
                "smtpport":int(getenv("SERVICE_EMAIL_SMTPPORT")),
                "senderid":getenv("SERVICE_EMAIL_SENDERID"),
                "senderpw":getenv("SERVICE_EMAIL_SENDERPW")
            },
            "access":{
                "secretkey":getenv("SERVICE_ACCESS_SECRETKEY"),
                "algorithm":getenv("SERVICE_ACCESS_ALGORITHM"),
                "expmin":int(getenv("SERVICE_ACCESS_EXPMIN"))
            },
        }
    },
}
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
app.add_middleware( APP.middleware )
app.mount(
    path="/static",
    app=staticfiles.StaticFiles(directory="app/core/static"),
    name="static_core"
)


# script
if __name__=="__main__":
    print()
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="127.0.0.1",
        port=9000,
        workers=1,
        reload=True
    )