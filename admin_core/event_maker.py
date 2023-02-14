from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from db.models import Event
from datetime import datetime


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
    :param duration: duration in seconds
    :param max_amount_of_people:
    :param admin_id: tg id of creator
    :return:
    """
    # TODO добавить информацию о группе (пока что нет этих частей)
    async with sm() as session:
        async with session.begin():
            q = insert(Event).values(event_type="Онлайн конференция",
                                     tg_alias=tg_username,
                                     name=name,
                                     start_datetime=beginning,
                                     duration=duration,
                                     max_amount_of_people=max_amount_of_people,
                                     created_id=admin_id,
                                     created_datetime=datetime.now())
            await session.execute(q)


async def new_offline_event(sm: sessionmaker,
                            name: str,
                            beginning: datetime,
                            max_amount_of_people: int,
                            admin_id: int):
    """
    Saves new offline event.

    :param sm:
    :param name: name of the event
    :param beginning: start datetime
    :param max_amount_of_people:
    :param admin_id: tg id of creator
    :return:
    """
    # TODO добавить информацию о группе (пока что нет этих частей)
    async with sm() as session:
        async with session.begin():
            q = insert(Event).values(event_type="Онлайн конференция",
                                     name=name,
                                     start_datetime=beginning,
                                     max_amount_of_people=max_amount_of_people,
                                     created_id=admin_id,
                                     created_datetime=datetime.now())
            await session.execute(q)


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
    :param duration: duration in seconds
    :param time_per_participant: how much time in seconds each personal chat takes
    :param admin_id: tg id of creator
    :return:
    """
    # TODO добавить информацию о группе (пока что нет этих частей)
    # TODO структура хранения будет другой; time_per_participant пока что просто некуда девать
    async with sm() as session:
        async with session.begin():
            q = insert(Event).values(event_type="Онлайн конференция",
                                     tg_alias=tg_username,
                                     name=name,
                                     start_datetime=beginning,
                                     duration=duration,
                                     created_id=admin_id,
                                     created_datetime=datetime.now())
            await session.execute(q)
