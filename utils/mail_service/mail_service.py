from fastapi import APIRouter, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from typing import Any, Dict, List, Optional
from dotenv import dotenv_values
from pathlib import Path
mailer = APIRouter()

class EmailSchema(BaseModel):
    subject: Optional[str]
    email: List[EmailStr]
    body: Dict[str, Any]

config_credentials = dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials['MAIL_USERNAME'],
    MAIL_PASSWORD=config_credentials['MAIL_PASSWORD'],
    MAIL_FROM=config_credentials['MAIL_FROM'],
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)

async def send_email_async(subject: str, email_to: List[str], body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        template_body=body,
        subtype='html',
        #######attachment files 
        # html="<img src='cid:logo_image'>",
        # subtype='html',
        # attachments=[
        #     {
        #         "file": "static/fastapi.png",
        #         "headers": {"Content-ID": "fastapi"},
        #         "mime_type": "image",
        #         "mime_subtype": "png",
        #     }
        # ],
    )
    fm = FastMail(conf)
    await fm.send_message(message,template_name="email_template.html")



def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=body,
        subtype='html',
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message,template_name="email_template.html")
