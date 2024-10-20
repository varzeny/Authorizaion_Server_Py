# email.py

# lib
from aiosmtplib import SMTP, send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# define
async def send_email(smtp_host:str, smtp_port:int, sender_addr:str, sender_pw:str, receiver_addr:str, subject:str, bodyData:str)->bool:

    # print(smtp_host, smtp_port, sender_addr, sender_pw, receiver_addr, subject, bodyData)

    result = None

    msg = MIMEMultipart()
    msg["From"] = sender_addr
    msg["To"] = receiver_addr
    msg["Subject"] = subject

    body = bodyData    # 뭔가 가공할거면 여기서
    msg.attach(MIMEText(body, "plain"))
    try:
        await send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=sender_addr,
            password=sender_pw,
            start_tls=True
        )
        result = True
    except Exception as e:
        print("ERROR from send_email : ", e)
        result = False
    finally:
        # await smtp_client.quit()
        return result



# "Your verify code has arrived."