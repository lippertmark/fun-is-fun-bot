import sqlalchemy
from db.models import *
import datetime
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import func, select, delete
from load import sm, engine


async def create_client_user(user_id: int, name: str, surname: str, username: str, created_datetime: datetime) -> bool:
    session = sm(bind=engine)
    new_user = UserClient(tg_id=user_id,
                          name=name,
                          surname=surname,
                          username=username,
                          created_datetime=created_datetime)
    try:
        session.add(new_user)
        await session.commit()
        return True
    except ProgrammingError:
        # TODO create logger message
        await session.rollback()
        return False


async def is_user(user_id: int) -> None | bool:
    session = sm(bind=engine)
    async with session:
        try:
            user = await session.execute(select(UserClient).where(UserClient.tg_id == user_id))
        except ProgrammingError:
            # TODO create logger message
            return False
    return user.one_or_none()


async def get_subscribes(user_id: int) -> dict | bool:
    session = sm(bind=engine)
    response = {}
    async with session:
        try:
            subs = await session.execute(select(Subscription).where(Subscription.user == user_id))
        except (ProgrammingError, ConnectionRefusedError):
            # TODO create logger message
            print(ProgrammingError, ConnectionRefusedError)
            return False
        else:
            for activity in subs:
                response[activity.Subscription.sport_club] = [activity.Subscription.type, activity.Subscription.sub_settings]
    return response


async def get_sport_types() -> dict | bool:
    session = sm(bind=engine)
    async with session:
        try:
            types = await session.execute(select(SportType))
        except (ProgrammingError, ConnectionRefusedError):
            # TODO create logger message
            return False
    result = {}
    for activity in types:
        result[activity.SportType.id] = activity.SportType.name
    return result


async def get_clubs(category: int) -> dict | bool:
    session = sm(bind=engine)
    async with session:
        try:
            clubs = await session.execute(select(SportClub).where(SportClub.sport_type == int(category)))
        except (ProgrammingError, ConnectionRefusedError):
            # TODO create logger message
            return False
    result = {}
    for activity in clubs:
        result[activity.SportClub.id] = activity.SportClub.name
    return result


async def get_club_info(club: str) -> dict | bool | None:
    session = sm(bind=engine)
    try:
        async with session:
            if str(club).isdigit():
                club = await session.execute(select(SportClub).where(SportClub.id == int(club)))
            else:
                club = await session.execute(select(SportClub).where(func.lower(SportClub.name) == func.lower(club)))
            if club is None:
                return None
            else:
                response = {}
                for activity in club:
                    response = {'id': activity.SportClub.id,
                                'name': activity.SportClub.name,
                                'sport_type': activity.SportClub.sport_type,
                                'description': activity.SportClub.description,
                                'photo': activity.SportClub.photo,
                                'base_subscription': await get_subscription_settings(activity.SportClub.base_subscription),
                                'standard_subscription': await get_subscription_settings(activity.SportClub.standart_subscription),
                                'premium_subscription': await get_subscription_settings(activity.SportClub.premium_subscription),
                                'subscriptions': [await get_subscription_settings(activity.SportClub.base_subscription),
                                                  await get_subscription_settings(activity.SportClub.standart_subscription),
                                                  await get_subscription_settings(activity.SportClub.premium_subscription)]
                                }
                    break
                return response
    except (ProgrammingError, ConnectionRefusedError):
        # TODO create logger message
        return False


# async def get_club_info_new(club: str) -> dict | bool | None:
#     db_session = await create_session()
#     async with db_session() as session:
#         try:
#             if str(club).isdigit():
#                 query = select(SportClub, SubscriptionSettings).where((SportClub.id == int(club)) &
#                                                                     (SportClub.base_subscription == SubscriptionSettings.id))
#                 response = await session.execute(query)
#                 subscribe = response.scalars().first()
#             else:
#                 query = select(SportClub).where(func.lower(SportClub.name) == func.lower(club))
#                 response = await session.execute(query)
#                 subscribe = response.scalars()
#             if club is None:
#                 return None
#             else:
#                 response = {}
#                 # for subscribe in club:
#                 response['id'] = subscribe.id,
#                 response['name'] = subscribe.name,
#                 response['sport_type'] = subscribe.sport_type,
#                 response['description'] = subscribe.description,
#                 response['photo'] = subscribe.photo,
#                 response['base_subscription'] = {
#                                 'id': subscribe.base_subscription,
#                                 'type': subscribe.subscription_type,
#                                 'includes': [],
#                                 'price': subscribe.price
#                             }
#                     response['standard_subscription'] = {
#                                     'id': subscribe.standart_subscription.id,
#                                     'type': subscribe.standart_subscription.subscription_type,
#                                     'includes': [],
#                                     'price': subscribe.standart_subscription.price
#                                 }
#                     response['premium_subscription'] = {
#                                     'id': subscribe.premium_subscription.id,
#                                     'type': subscribe.premium_subscription.subscription_type,
#                                     'includes': [],
#                                     'price': subscribe.premium_subscription.price
#                                 }
#                     response['subscriptions'] = [
#                         response['base_subscription'],
#                         response['standard_subscription'],
#                         response['premium_subscription']
#                       ]
#                 return response
#         except (ProgrammingError, ConnectionRefusedError):
#             # TODO create logger message
#             return False


async def get_subscription_settings(subscription_settings_id):
    session = sm(bind=engine)
    response = {}
    async with session:
        settings = await session.execute(select(SubscriptionSettings).where(
            SubscriptionSettings.id == subscription_settings_id))
        await session.commit()
        list_of_includes = []
        for activity in settings:
            if activity.SubscriptionSettings.videochat:
                list_of_includes.append('Видеочат')
            if activity.SubscriptionSettings.conference:
                list_of_includes.append('Онлайн конференция')
            if activity.SubscriptionSettings.offline_event:
                list_of_includes.append('Оффлайн мероприятие')
            response['id'] = activity.SubscriptionSettings.id
            response['type'] = activity.SubscriptionSettings.subscription_type
            response['includes'] = list_of_includes
            response['price'] = activity.SubscriptionSettings.price

    return response


async def add_subscription(user_id, type, sport_club, sub_settings, date):
    # TODO thinking about what is subscription not created
    session = sm(bind=engine)
    new_subscription = Subscription(user=user_id, type=type, sport_club=sport_club, sub_settings=sub_settings,
                                    expired_date=date)
    async with session:
        try:
            session.add(new_subscription)
            await session.commit()
        except (ProgrammingError, ConnectionRefusedError):
            await session.rollback()
            # TODO create logger message
            return False
    return True


async def get_club_name(club: int) -> str | bool:
    session = sm(bind=engine)
    async with session:
        try:
            club = await session.execute(select(SportClub.name).where(SportClub.id == int(club)))
        except (ProgrammingError, ConnectionRefusedError):
            # TODO create logger message
            return False
    for activity in club:
        activity = str(activity)
        res = activity.split('\'')[1]
        return res


async def get_all_events(club_id: int, type: str) -> dict | bool:
    session = sm(bind=engine)
    response = {}
    async with session:
        try:
            all_events = await session.execute(select(Event).where(Event.club == int(club_id), Event.event_type == type))
        except (ProgrammingError, ConnectionRefusedError):
            # TODO create logger message
            return False
        for event in all_events:
            if event.Event.event_type != 'Видеочат' or await get_slots(event.Event.id):
                if event.Event.start_datetime + datetime.timedelta(minutes=event.Event.duration) > datetime.datetime.now():
                    response[event.Event.id] = {
                        'id': event.Event.id,
                        'event_type': event.Event.event_type,
                        'club': event.Event.club,
                        'name': event.Event.name,
                        'tg_alias': event.Event.tg_alias,
                        'start_datetime': event.Event.start_datetime,
                        'duration': event.Event.duration,
                        'max_amount_of_people': event.Event.max_amount_of_people,
                        'created_datetime': event.Event.created_datetime,
                        'created_id': event.Event.created_id,
                        'telegram_group_id': event.Event.telegram_group_id,
                        'telegram_group_invitation_link': event.Event.telegram_group_invitation_link,
                    }
    return response


async def get_event(event_id: int) -> dict | bool:
    session = sm(bind=engine)
    response = {}
    async with session:
        try:
            event_req = await session.execute(select(Event).where(Event.id == int(event_id)))
            for event in event_req:
                response = {
                    'id': event.Event.id,
                    'event_type': event.Event.event_type,
                    'club': event.Event.club,
                    'name': event.Event.name,
                    'tg_alias': event.Event.tg_alias,
                    'start_datetime': event.Event.start_datetime,
                    'duration': event.Event.duration,
                    'max_amount_of_people': event.Event.max_amount_of_people,
                    'created_datetime': event.Event.created_datetime,
                    'created_id': event.Event.created_id,
                    'telegram_group_id': event.Event.telegram_group_id,
                    'telegram_group_invitation_link': event.Event.telegram_group_invitation_link,
                }
        except (ProgrammingError, ConnectionRefusedError):
            # TODO create logger message
            print("ERROR")
            return False
    return response


async def get_bookings(user_id):
    session = sm(bind=engine)
    result = {}
    async with session:
        try:
            bookings = await session.execute(select(BookingEvent, Event, SportClub).
                                             join(Event, BookingEvent.event_id == Event.id).
                                             join(SportClub, Event.club == SportClub.id)
                                             .where(BookingEvent.user_id == int(user_id)))
            for booking in bookings:
                if booking.Event.start_datetime + datetime.timedelta(minutes=booking.Event.duration) > datetime.datetime.now():
                    result[booking.BookingEvent.event_id] = [booking.Event.name, booking.SportClub.name]
        except (ProgrammingError, ConnectionRefusedError):
            return False
    return result


async def book_event(user_id, event_id, booking_datetime, slot_id):
    session = sm(bind=engine)
    new_booking = BookingEvent(user_id=user_id, event_id=event_id, booking_datetime=booking_datetime, slot_id=int(slot_id))
    try:
        session.add(new_booking)
        await session.commit()
        return True
    except ProgrammingError:
        # TODO create logger message
        await session.rollback()
        return False


async def cancel_booking(user_id, booking_id):
    session = sm(bind=engine)
    try:
        await session.execute(delete(BookingEvent).where(BookingEvent.event_id == int(booking_id),
                                                         BookingEvent.user_id == int(user_id)))

        slots = await session.execute(select(Slots).where(Slots.user_id == int(user_id),
                                                          Slots.event_id == int(booking_id)))
        slot = slots.scalars().one()
        slot.user_id = 0
        await session.commit()
    except (ProgrammingError, ConnectionRefusedError):
        return False


async def get_chatId(event_id):
    session = sm(bind=engine)
    async with session:
        try:
            chats = await session.execute(select(Chat).where(Chat.event == int(event_id)))
            for chat in chats:
                return chat.Chat.chat_id
        except (ProgrammingError, ConnectionRefusedError):
            return False


async def unsubscribe(user_id, club_id):
    session = sm(bind=engine)
    try:
        await session.execute(delete(Subscription).where(Subscription.user == int(user_id),
                                                         Subscription.sport_club == int(club_id)))
        await session.commit()
    except (ProgrammingError, ConnectionRefusedError):
        return False


async def get_slots(event_id):
    session = sm(bind=engine)
    async with session:
        try:
            response = {}
            slots = await session.execute(select(Slots).where(Slots.event_id == int(event_id), Slots.user_id == 0))
            for slot in slots:
                if slot.Slots.start_time > datetime.datetime.now():
                    response[slot.Slots.id] = [slot.Slots.start_time.strftime("%H:%M"), slot.Slots.end_time.strftime("%H:%M")]
        except (ProgrammingError, ConnectionRefusedError):
            return False
    return response


async def book_slot(user_id, slot_id):
    session = sm(bind=engine)
    async with session:
        try:
            slots = await session.execute(select(Slots).where(Slots.id == int(slot_id)))
            user = slots.scalars().one()
            if user.user_id == 0:
                user.user_id = user_id
                await session.commit()
            else:
                return 400
        except (ProgrammingError, ConnectionRefusedError):
            return False


async def get_subscriptions():
    session = sm(bind=engine)
    async with session:
        try:
            response = []
            subs = await session.execute(select(Subscription))
            users = subs.scalars().all()
            await session.commit()
            for user in users:
                response.append(user.user_id)
        except (ProgrammingError, ConnectionRefusedError):
            return False
    return response


async def get_slot(user_id):
    session = sm(bind=engine)
    response = []
    async with session:
        try:
            slots = await session.execute(select(Slots).where(Slots.user_id == int(user_id)))
            for slot in slots:
                response = [slot.Slots.start_time, slot.Slots.end_time]
        except (ProgrammingError, ConnectionRefusedError):
            return False
    return response


# async def create_events(club):
#     local_session = sm(bind=engine)
#     event_1 = Event(event_type='Оффлайн мероприятие', club=club, name='первый', tg_alias='lippert_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=15,
#                     created_datetime=datetime.datetime.now(), created_id=542643041, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     event_2 = Event(event_type='Оффлайн мероприятие', club=club, name='Второй', tg_alias='lippert_ne_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=1000,
#                     created_datetime=datetime.datetime.now(), created_id=542643041, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     event_3 = Event(event_type='Оффлайн мероприятие', club=club, name='Третий!', tg_alias='lippert_ne_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=5,
#                     created_datetime=datetime.datetime.now(), created_id=542643041, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     event_4 = Event(event_type='Оффлайн мероприятие', club=club, name='Четвертый', tg_alias='lippert_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=30,
#                     created_datetime=datetime.datetime.now(), created_id=542643041, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     try:
#         local_session.add(event_1)
#         local_session.add(event_2)
#         local_session.add(event_3)
#         local_session.add(event_4)
#         await local_session.commit()
#         return True
#     except ProgrammingError:
#         # TODO create logger message
#         await local_session.rollback()
#         return False
