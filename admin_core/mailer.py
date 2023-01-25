from datetime import datetime, timedelta
from random import randint
from config import CODE_LENGTH

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TIME_FORMAT = "%d-%m-%Y %H:%M:%S"


async def send_code(email: str) -> (str, datetime):
    code = ''.join(str(randint(0, 9)) for _ in range(CODE_LENGTH))
    created = datetime.now()
    expires = created + timedelta(minutes=10)

    print(code)
    # TODO: actually send the code :D

    return code, created.strftime(TIME_FORMAT), expires.strftime(TIME_FORMAT)

