from config import CODE_LENGTH, EMAIL_SENDER, EMAIL_SECRET
from datetime import datetime, timedelta
from typing import Dict, Tuple
from random import randint

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TIME_FORMAT = "%d-%m-%Y %H:%M:%S"


async def send_letter(email: str, subject: str, html_template: str, data: Dict) -> None:
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
    code = ''.join(str(randint(0, 9)) for _ in range(CODE_LENGTH))
    created = datetime.now()
    expires = created + timedelta(minutes=10)

    with open("admin_core/code_email.html", "r", encoding='utf-8') as code_email_template:
        template = code_email_template.read()

    await send_letter(email, "аутентификация в FanIsFun-admins",
                      template, {"code": code, "expires": expires.strftime("%H:%M")})

    return code, created.strftime(TIME_FORMAT), expires.strftime(TIME_FORMAT)

