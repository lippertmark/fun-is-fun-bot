import datetime
import time

from db_client.models import *
from sqlalchemy import func


def create_client_user(tg_id, name, surname, username, created_datetime, state=''):
    local_session = Session(bind=engine)
    new_user = UserClient(tg_id=tg_id, name=name, surname=surname, username=username, created_datetime=created_datetime, state=state)
    local_session.add(new_user)
    local_session.commit()


def all_sport_types():
    local_session = Session(bind=engine)
    sport_types = local_session.query(SportType).all()
    response = []
    for sport_type in sport_types:
        if get_list_of_sport_clubes_by_type(sport_type.id):
            response.append([sport_type.id, sport_type.name])
    local_session.commit()
    return response


def get_list_of_sport_clubes_by_type(sport_type_id):
    local_session = Session(bind=engine)
    sport_clubs = local_session.query(SportClub).filter(SportClub.sport_type == sport_type_id)
    response = []
    for sport_club in sport_clubs:
        response.append([sport_club.id, sport_club.name])
    local_session.commit()
    return response


def add_subscription(tg_id, type, sport_club_id):
    """"
        Add info about subscription to database
        :param tg_id: user id
        :param type: type of subscription
        :param sport_club_id: id of sport club
        :return:
    """
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


def get_category_name(category_id):
    local_session = Session(bind=engine)
    category = local_session.query(SportType).filter(SportType.id == category_id)
    local_session.commit()
    return category[0].name


def is_user(user_id):
    local_session = Session(bind=engine)
    users = local_session.query(UserClient).filter(UserClient.tg_id == user_id)
    local_session.commit()
    for user in users:
        return user.tg_id


def get_subscription_settings(subscription_settings_id):
    response = {}
    local_session = Session(bind=engine)

    settings = local_session.query(SubscriptionSettings).filter(
        SubscriptionSettings.id == subscription_settings_id).first()
    list_of_includes = []
    if settings.videochat:
        list_of_includes.append('Видеочат')
    if settings.conference:
        list_of_includes.append('Конференция')
    if settings.offline_event:
        list_of_includes.append('Оффлайн мероприятие')
    response['id'] = settings.id
    response['includes'] = list_of_includes
    response['subscription_type'] = settings.subscription_type
    response['price'] = settings.price
    local_session.commit()
    return response


def get_club_info(club):
    local_session = Session(bind=engine)
    if str(club).isdigit():
        club = local_session.query(SportClub).filter(SportClub.id == club).all()
    else:
        club = local_session.query(SportClub).filter(func.lower(SportClub.name) == func.lower(club)).all()
    local_session.commit()
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


def get_bookings(user_id):
    local_session = Session(bind=engine)
    bookings = local_session.query(BookingEvent).filter(BookingEvent.user_id == user_id).all()
    result = []
    for booking in bookings:
        result.append(booking.event_id)
    local_session.commit()
    return result


def get_absolutely_all_events():
    local_session = Session(bind=engine)
    all_events = local_session.query(Event)
    result = {}
    for event in all_events:
        result[event.id] = {'name': event.name, 'club': event.club}
    local_session.commit()
    return result


def unsubscribe(user_id, club_id):
    local_session = Session(bind=engine)
    print("Пользователь ", user_id, "отписался от ", club_id)
    local_session.query(Subscription).filter(Subscription.user == user_id, Subscription.sport_club == club_id).delete()
    local_session.commit()

# create_client_user(338600505, 'Mark', 'Lippert', datetime.datetime.now(), '')
# print(all_sport_types())
# add_sport_types()
# print(get_list_of_sport_clubes_by_type(1))
# print(get_list_of_sport_clubes_by_type(2))
# add_subscription(338600505, 'base', 7)

# эти функции раскоменьть, запусти и они создадут какие-то объекты в бд,
# типа типы спортов, настройки и клубы
# create_client_user(338600505, 'Mark', 'Lippert', datetime.datetime.now(), '')
# create_sport_types()
# create_subscription_settings()
# create_sport_clubs()
# all_sport_types()

# create_events()

# unsubscribe(542643041, 3)


