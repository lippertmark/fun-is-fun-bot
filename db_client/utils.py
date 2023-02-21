from models import *
import datetime
import time

from db_client.models import *
from sqlalchemy import func

# from decl import Session, UserClientCopy, engine


def create_client_user(tg_id, username, name, surname, created_datetime, state=''):
    local_session = Session(bind=engine)
    new_user = UserClient(tg_id=tg_id, name=name, surname=surname, username=username, created_datetime=created_datetime, state=state)
    local_session.add(new_user)
    local_session.commit()



def create_admin_user(tg_id, name, surname, email, created_datetime, state=''):
    local_session = Session(bind=engine)

    new_user = UserAdmin(tg_id=tg_id, name=name, surname=surname, email=email, created_datetime=created_datetime, state=state)
    local_session.add(new_user)
    local_session.commit()

def all_sport_types():
    '''

    :return: all types of sport
    '''
    local_session = Session(bind=engine)
    sport_types = local_session.query(SportType).all()
    response = []
    for sport_type in sport_types:
        if get_list_of_sport_clubes_by_type(sport_type.id):
            response.append([sport_type.id, sport_type.name])
    local_session.commit()
    return response


def create_sport_types():
    '''
    you can use this method to initialize sport types
    :return:
    '''
    local_session = Session(bind=engine)

    football = SportType(name='Футбол')
    hockey = SportType(name='Хоккей')
    local_session.add(football)
    local_session.add(hockey)
    local_session.commit()


def create_subscription_settings():
    local_session = Session(bind=engine)
    base = SubscriptionSettings(subscription_type='base', videochat=True, conference=False, offline_event=False,
                                price=10000)
    standart = SubscriptionSettings(subscription_type='standart', videochat=True, conference=True, offline_event=False,
                                    price=30000)
    premium = SubscriptionSettings(subscription_type='premium', videochat=True, conference=True, offline_event=True,
                                   price=50000)
    local_session.add(base)
    local_session.add(standart)
    local_session.add(premium)
    local_session.commit()


def create_sport_clubes():
    '''
    you can use this method to initialize sport types
    :return:
    '''
    local_session = Session(bind=engine)

    ak_bars = SportClub(name='Ак барс', sport_type=2, base_subscription=1, standart_subscription=2,
                        premium_subscription=3)
    zenit = SportClub(name='Зенит', sport_type=1, base_subscription=1, standart_subscription=2, premium_subscription=3)
    rubin = SportClub(name='Рубин', sport_type=1, base_subscription=1, standart_subscription=2, premium_subscription=3)
    local_session.add(ak_bars)
    local_session.add(zenit)
    local_session.add(rubin)
    local_session.commit()


def get_list_of_sport_clubes_by_type(sport_type_id):
    '''
    :param sport_type_id:
    :return: list of clubs of this sport type
    '''
    local_session = Session(bind=engine)
    sport_types = local_session.query(SportClub).filter(SportClub.sport_type == sport_type_id)
    response = []
    for sport_type in sport_types:
        response.append([sport_type.id, sport_type.name])
    local_session.commit()
    return response


def add_subscription(tg_id, type, sport_club_id):
    '''
    Add info about subscription to data base
    :param tg_id: user id
    :param type: type of subscription
    :param sport_club_id: id of sport club
    :return:
    '''
    local_session = Session(bind=engine)

    new_subscription = Subscription(user=tg_id, type=type, sport_club=sport_club_id)
    local_session.add(new_subscription)
    local_session.commit()


def get_subscribes(tg_id):
    local_session = Session(bind=engine)
    subs = local_session.query(Subscription).filter(Subscription.user == tg_id)
    result = {}
    for sub in subs:
        result[sub.sport_club] = sub.type
    local_session.commit()
    return result


def get_club_name(club_id):
    local_session = Session(bind=engine)
    sport_type = local_session.query(SportClub).filter(SportClub.id == club_id)

    local_session.commit()
    return sport_type[0].name


def get_user(tg_id):
    local_session = Session(bind=engine)

    user = local_session.query(UserClient).filter(UserClient.tg_id == tg_id).all()
    if len(user) == 0:
        return None
    else:
        return {
            'tg_id': user[0].tg_id,
            'username': user[0].username,
            'name': user[0].name,
            'surname': user[0].surname,
            'created_datetime': user[0].created_datetime,
            'state': user[0].state
        }




def get_subscription_settings(subscription_settings_id):
        '''

        :param subscription_settings_id:
        :return: info about price, what include and type
        '''
        response = {}
        local_session = Session(bind=engine)

        settings = local_session.query(SubscriptionSettings).filter(SubscriptionSettings.id ==subscription_settings_id).first()
        list_of_includes = []
        if settings.videochat == True:
                list_of_includes.append('videochat')
        if settings.conference == True:
                list_of_includes.append('conference')
        if settings.offline_event == True:
                list_of_includes.append('offline_event')
        response['id'] = settings.id
        response['include'] = list_of_includes
        response['subscription_type'] = settings.subscription_type
        response['price'] = settings.price
        return response

def get_club(club_id):
    '''

    :param club_id:
    :return: None - if club does not exist, else return dict with info about club
    '''
    local_session = Session(bind=engine)

    club = local_session.query(SportClub).filter(SportClub.id == club_id).all()
    if len(club) == 0:
        return None
    else:
        response = {'id': club[0].id,
                    'name': club[0].name,
                    'sport_type': club[0].sport_type,
                    'description': club[0].description,
                    'photo': club[0].photo,
                    'base_subscription': get_subscription_settings(club[0].base_subscription),
                    'standard_subscription': get_subscription_settings(club[0].standart_subscription),
                    'premium_subscription': get_subscription_settings(club[0].premium_subscription),
                    'subscriptions': [get_subscription_settings(club[0].base_subscription),
                                      get_subscription_settings(club[0].standart_subscription),
                                      get_subscription_settings(club[0].premium_subscription)]
                    }
        return response


def get_all_events(club_id, type1):
    local_session = Session(bind=engine)
    all_events = local_session.query(Event).filter(Event.club == club_id, Event.event_type == type1)
    response = {}
    local_session.commit()
    for event in all_events:
        # if event.start_datetime > datetime.datetime.now():
            response[event.id] = {
                'id': event.id,
                'event_type': event.event_type,
                'club': event.club,
                'name': event.name,
                'tg_alias': event.tg_alias,
                'start_datetime': event.start_datetime,
                'duration': event.duration,
                'max_amount_of_people': event.max_amount_of_people,
                'created_datetime': event.created_datetime,
                'created_id': event.created_id,
                'telegram_group_id': event.telegram_group_id,
                'telegram_group_invitation_link': event.telegram_group_invitation_link,
            }
    return response

def get_all_time_delete():
    local_session = Session(bind=engine)
    all_time_delete = local_session.query(TimeDelete).all()
    response = []
    for item in all_time_delete:
        response.append({
            'chat_id': item.chat_id,
            'user_id': item.user_id,
            'start_time': item.start_time,
            'end_time': item.end_time,
        })


def get_event(event_id):
    local_session = Session(bind=engine)

    event = local_session.query(Event).filter(Event.id == event_id).all()
    local_session.commit()
    if len(event) == 0:
        return None
    else:
        event = event[0]
        return {
            'id': event.id,
            'event_type': event.event_type,
            'club': event.club,
            'name': event.name,
            'tg_alias': event.tg_alias,
            'start_datetime': event.start_datetime,
            'duration': event.duration,
            'max_amount_of_people': event.max_amount_of_people,
            'created_datetime': event.created_datetime,
            'created_id': event.created_id,
            'telegram_group_id': event.telegram_group_id,
            'telegram_group_invitation_link': event.telegram_group_invitation_link,
        }


def book_event(user_id, event_id, booking_datetime):
    local_session = Session(bind=engine)
    new_booking = BookingEvent(user_id=user_id, event_id=event_id, booking_datetime=booking_datetime)
    local_session.add(new_booking)
    local_session.commit()



# create_client_user(338600505, 'Mark', 'Lippert', datetime.datetime.now(), '')
# print(all_sport_types())

def get_absolutely_all_events():
    local_session = Session(bind=engine)
    all_events = local_session.query(Event)
    result = {}
    for event in all_events:
        result[event.id] = {'name': event.name, 'club': event.club}
    local_session.commit()
    return result

# print(get_user(338600505))
# print(get_club(4))

def unsubscribe(user_id, club_id):
    local_session = Session(bind=engine)
    print("Пользователь ", user_id, "отписался от ", club_id)
    local_session.query(Subscription).filter(Subscription.user == user_id, Subscription.sport_club == club_id).delete()
    local_session.commit()


# эти функции раскоменьть, запусти и они создадут какие-то объекты в бд,
# типа типы спортов, настройки и клубы
# create_client_user(338600505, 'Mark', 'Lippert', datetime.datetime.now(), '')
# create_sport_types()
# create_subscription_settings()
# create_sport_clubes()
# create_sport_clubs()
# all_sport_types()
# create_events()
# unsubscribe(542643041, 3)

