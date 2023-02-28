import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from random import randint
from typing import Dict

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TIME_FORMAT = "%d-%m-%Y %H:%M:%S"
CODE_LENGTH = 6
dotenv_path = os.path.join(os.path.dirname(__file__), '..', ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_SECRET = os.getenv('EMAIL_SECRET')


async def send_letter(email: str, subject: str, html_template: str, data: Dict):
    """
    Simple email sender.
    Replaces {{key}} in html with corresponding value from data

    :param email: where to
    :param subject: subject of the letter
    :param html_template:
    :param data:
    :return:
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = email

    text = str(data)

    # very bad approach, but I will leave it as is for now
    # if some good engine (Jinja / Django) will be added to the project, this thing should be updated definitely
    html = html_template
    for key in data:
        html = html.replace("{{" + key + "}}", data[key])

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.ehlo()
    s.login(EMAIL_SENDER, EMAIL_SECRET)

    s.sendmail(EMAIL_SENDER, email, msg.as_string())
    s.quit()


async def send_code(email: str) -> (str, datetime, datetime):
    """
    Generates and sends verification code to provided email.
    Returns code, time of creation, expiration time.

    :param email:
    :return:
    """
    code = ''.join(str(randint(0, 9)) for _ in range(CODE_LENGTH))
    created = datetime.now()
    expires = created + timedelta(minutes=10)

    with open("admin_core/code_email.html", "r", encoding='utf-8') as code_email_template:
        template = code_email_template.read()

    await send_letter(email, "аутентификация в FanIsFun-admins",
                      template, {"code": code, "expires": expires.strftime("%H:%M")})

    return code, created.strftime(TIME_FORMAT), expires.strftime(TIME_FORMAT)

