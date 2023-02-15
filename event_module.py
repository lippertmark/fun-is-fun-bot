from config import MANAGER_BOT_TOKEN
from db_client.models import *
import requests
import datetime
import pytz
import time


def do_request(token, method_name, method, data):
    if not data:
        data = dict()
    link = f'https://api.telegram.org/bot{token}/{method_name}'
    if method == 'post':
        return requests.post(url=link, data=data).json()
    elif method == 'get':
        return requests.get(url=link, data=data).json()


def add_chats_to_db():
    chats = [
        {'name': 'Пространство 1', 'chat_id': -1001737207692},
        {'name': 'Пространство 2', 'chat_id': -1001884920763},
    ]
    local_session = Session(bind=engine)

    for chat in chats:
        local_session.add(Chat(chat_id=chat['chat_id'], name=chat['name']))

    local_session.commit()


def give_chat_for_event(event_id):
    """
    Выделяет чат для мероприятия
    :param event_id:
    :return:
    """
    local_session = Session(bind=engine)
    chat = local_session.query(Chat).filter(Chat.event == 0).first()
    # chat['event'] = event_id
    chat_id = chat.chat_id
    local_session.query(Chat).filter(Chat.chat_id == chat_id).update(values={'event': event_id})
    local_session.commit()
    return {'chat_id': chat_id, 'name': chat.name}


def give_link_to_invite(chat_id, user_id):
    """
    Дает ссылку-приглашение в чат мероприятия
    :param chat_id:
    :param user_id:
    :return:
    """
    date_expired = datetime.datetime.now(pytz.timezone("Europe/Moscow")) + datetime.timedelta(minutes=5)
    date_expired_timestamp = int(time.mktime(date_expired.timetuple()))
    response = do_request(token=MANAGER_BOT_TOKEN, method_name='createChatInviteLink',
                          method='post', data={'chat_id': chat_id, 'expire_date': date_expired_timestamp})
    link = response['result']['invite_link']
    local_session = Session(bind=engine)
    local_session.add(LinkForUserToChat(chat_id=chat_id, user_id=user_id, link=link, date_expired=date_expired))
    local_session.commit()
    return link


def check_user_is_approved(chat_id, user_id):
    """
    Проверка может ли человек зайти в чат
    :param chat_id:
    :param user_id:
    :return:
    """
    date_now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    local_session = Session(bind=engine)
    response = local_session.query(LinkForUserToChat).filter(LinkForUserToChat.chat_id == chat_id,
                                                             LinkForUserToChat.user_id == user_id)
    for item in response:
        if item.date_expired > date_now:
            return True
    return False


if __name__ == "__main__":
    add_chats_to_db()

    print(give_link_to_invite(-1001884920763, user_id=338600505))
    print(check_user_is_approved(-1001884920763, 338600505))
    print(check_user_is_approved(-1001884920763, 338600506))

    # method_name = 'createChatInviteLink'
    # data = {
    #     'chat_id': -1001860272929,
    # }
    # link = f'https://api.telegram.org/bot{token}/{method_name}'
    # print(requests.post(url=link, data=data).json()['result'])

    # print(link)

    # https://t.me/random_int_bot
    # r = requests.get()
    # https://t.me/+ke6tOryup6dkZTgy
    # test for fan