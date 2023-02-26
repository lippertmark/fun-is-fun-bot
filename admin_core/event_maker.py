from admin_core.customers import get_affiliated_club
from event_module import give_chat_for_event
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, update
from datetime import datetime, timedelta
from db.models import Event, Slots


async def new_online_conference(sm: sessionmaker,
                                tg_username: int,
                                name: str,
                                beginning: datetime, duration: int,
                                max_amount_of_people: int,
                                admin_id: int):
    """
    Saves new online conference.

    :param sm:
    :param tg_username: performer alias
    :param name: name of the event
    :param beginning: start datetime
    :param duration: duration in minutes
    :param max_amount_of_people:
    :param admin_id: tg id of creator
    :return: event_id
    """
    async with sm() as session:
        async with session.begin():
            q = insert(Event) \
                .values(event_type="Онлайн конференция",
                        tg_alias=tg_username,
                        name=name,
                        club=await get_affiliated_club(sm, admin_id),
                        start_datetime=beginning,
                        duration=duration,
                        max_amount_of_people=max_amount_of_people,
                        created_id=admin_id,
                        created_datetime=datetime.now()) \
                .returning(Event.id)
            event_id = await session.execute(q)
            event_id = event_id.one_or_none().id
            # obtaining chat_id
            try:
                chat = give_chat_for_event(event_id)
                q = update(Event) \
                    .values(telegram_group_id=str(chat.get('chat_id'))) \
                    .where(Event.id == event_id)
                await session.execute(q)
            except:
                pass
    return event_id


async def new_offline_event(sm: sessionmaker,
                            tg_username: str,
                            name: str,
                            beginning: datetime,
                            duration: int,
                            max_amount_of_people: int,
                            admin_id: int):
    """
    Saves new offline event.

    :param sm:
    :param tg_username: performer alias
    :param name: name of the event
    :param beginning: start datetime
    :param duration: duration in minutes
    :param max_amount_of_people:
    :param admin_id: tg id of creator
    :return: event_id
    """
    async with sm() as session:
        async with session.begin():
            q = insert(Event) \
                .values(event_type="Оффлайн мероприятие",
                        club=await get_affiliated_club(sm, admin_id),
                        tg_alias=tg_username,
                        name=name,
                        start_datetime=beginning,
                        duration=duration,
                        max_amount_of_people=max_amount_of_people,
                        created_id=admin_id,
                        created_datetime=datetime.now()) \
                .returning(Event.id)
            event_id = await session.execute(q)
            event_id = event_id.one_or_none().id
            # obtaining chat_id
            try:
                chat = give_chat_for_event(event_id)
                q = update(Event) \
                    .values(telegram_group_id=str(chat.get('chat_id'))) \
                    .where(Event.id == event_id)
                await session.execute(q)
            except:
                pass
    return event_id


async def new_videoconference(sm: sessionmaker,
                              tg_username: int,
                              name: str,
                              beginning: datetime, duration: int,
                              time_per_participant: int,
                              admin_id: int):
    """
    Saves new online conference.

    :param sm:
    :param tg_username: performer alias
    :param name: name of the event
    :param beginning: start datetime
    :param duration: duration in minutes
    :param time_per_participant: how much time in minutes each personal chat takes
    :param admin_id: tg id of creator
    :return: event_id
    """
    if time_per_participant == 0:
        max_people = 0
    else:
        max_people = duration // time_per_participant

    async with sm() as session:
        async with session.begin():
            # default activity info
            q = insert(Event) \
                .values(event_type="Видеочат",
                        club=await get_affiliated_club(sm, admin_id),
                        tg_alias=tg_username,
                        name=name,
                        start_datetime=beginning,
                        duration=duration,
                        max_amount_of_people=max_people,
                        created_id=admin_id,
                        created_datetime=datetime.now()) \
                .returning(Event.id)
            event_id = await session.execute(q)
            event_id = event_id.one_or_none().id
            # obtaining chat_id
            try:
                chat = give_chat_for_event(event_id)
                q = update(Event) \
                    .values(telegram_group_id=str(chat.get('chat_id'))) \
                    .where(Event.id == event_id)
                await session.execute(q)
            except:
                pass

            # generating time slots - list of models.Slot
            slots = []
            base_time = beginning
            for i in range(max_people):
                new_time = base_time + timedelta(minutes=time_per_participant)
                slots.append(Slots(start_time=base_time, end_time=new_time, event_id=event_id, user=0))
                base_time = new_time

            # saving slots info
            session.add_all(slots)
            await session.commit()

    return event_id
