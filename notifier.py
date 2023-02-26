import os
from schedule import every, repeat, run_pending
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from db.models import BookingEvent, Event, Slots
from datetime import datetime, timedelta
from sortedcontainers import SortedSet
from aiogram import Bot
from dotenv import load_dotenv
import asyncio
import time


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
TOKEN_TELEGRAM_CLIENT = os.getenv('TOKEN_TELEGRAM_CLIENT')
TOKEN_TELEGRAM_ADMIN = os.getenv('TOKEN_TELEGRAM_ADMIN')


async def event_notification(event_id: int):
    """
    Selects everyone wha has to receive notification by event_id and sends them message.
    :param event_id:
    """
    with sm() as session:
        with session.begin():
            q = select(BookingEvent.user_id).where(BookingEvent.event_id == event_id)
            participants = session.execute(q, execution_options={"prebuffer_rows": True})
            q = select(Event).where(Event.id == event_id)
            event_info = session.execute(q, execution_options={"prebuffer_rows": True})
            event_info = event_info.one_or_none()

    reminder_msg = f'Привет!\nСпешим напомнить о мероприятии ' \
                   f'"{event_info.Event.name}" ({event_info.Event.event_type.lower()}) в ' \
                   f'{event_info.Event.start_datetime.strftime("%H:%M")} ' \
                   f'(через <b>{(event_info.Event.start_datetime - datetime.now()).seconds // 60 + 1}</b> минут)'

    if event_info.Event.event_type.lower() != "видеочат":
        for participant in participants:  # messaging participants
            await user_notifier.send_message(*participant, reminder_msg)

    # also messaging admin
    await admin_notifier.send_message(event_info.Event.created_id, reminder_msg)


async def videochat_notification(slot_id: int):
    """
    Selects everyone wha has to receive notification by slot_id and sends them message.
    :param slot_id:
    """
    with sm() as session:
        with session.begin():
            q = select(Slots).where(Slots.id == slot_id)
            participant = session.execute(q, execution_options={"prebuffer_rows": True})
            participant = participant.one_or_none()
            q = select(Event).where(Event.id == participant.Slots.event_id)
            event_info = session.execute(q, execution_options={"prebuffer_rows": True})
            event_info = event_info.one_or_none()

    reminder_msg = f'Привет!\nСпешим напомнить о видеочате ' \
                   f'"{event_info.Event.name}" в ' \
                   f'{participant.Slots.start_time.strftime("%H:%M")} ' \
                   f'(через <b>{(participant.Slots.start_time - datetime.now()).seconds // 60 + 1}</b> минут)'

    # messaging participant
    if participant.Slots.user != 0:
        await user_notifier.send_message(participant.Slots.user, reminder_msg)


async def by_minute_checker():
    """
    Minutely checks if notifications should be sent now
    """
    global reminders, videoslots
    time_now = datetime.now()
    while reminders and reminders[0][1] <= time_now:
        event = reminders.pop(0)
        await event_notification(event[0])
    while videoslots and videoslots[0][1] <= time_now:
        slot = videoslots.pop(0)
        await videochat_notification(slot[0])


@repeat(every(1).minutes)
def run_by_minute_checker():
    """
    Workaround, schedule does not support async initially
    """
    asyncio.run(by_minute_checker())


@repeat(every(5).minutes)
def update_events():
    """
    Every N minutes updates reminders, gets events in period (now, now + 1.5h]
    """
    run_by_minute_checker()  # to make sure notifications for current minute will be sent
    time_now = datetime.now()
    bound_time = time_now + timedelta(minutes=90)
    with sm() as session:
        with session.begin():
            q = select(Event) \
                .where(Event.start_datetime.between(time_now, bound_time))
            events = session.execute(q, execution_options={"prebuffer_rows": True})
            q = select(Slots).where(Slots.start_time.between(time_now, bound_time))
            slots = session.execute(q, execution_options={"prebuffer_rows": True})

    new_reminders = SortedSet(key=lambda x: x[1])
    time_now = datetime.now()

    for event in events:
        start_time = event.Event.start_datetime
        # making sure that notification will be sent in the future, not in the past
        if start_time - timedelta(minutes=5) >= time_now:
            new_reminders.add((event.Event.id, start_time - timedelta(minutes=5)))
        if start_time - timedelta(minutes=60) >= time_now:
            new_reminders.add((event.Event.id, start_time - timedelta(minutes=60)))

    new_slots = SortedSet(key=lambda x: x[1])
    time_now = datetime.now()
    for slot in slots:
        start_time = slot.Slots.start_time
        # making sure that notification will be sent in the future, not in the past
        if start_time - timedelta(minutes=5) >= time_now:
            new_slots.add((slot.Slots.id, start_time - timedelta(minutes=5)))
        if start_time - timedelta(minutes=60) >= time_now:
            new_slots.add((slot.Slots.id, start_time - timedelta(minutes=60)))

    global reminders, videoslots
    reminders = new_reminders.copy()
    videoslots = new_slots.copy()


if __name__ == "__main__":
    # db initialization
    db_url = URL.create("postgresql",
                        host=os.getenv('DB_HOST'),
                        port=os.getenv('DB_PORT'),
                        username=os.getenv('DB_USERNAME'),
                        password=os.getenv('DB_PASSWORD'),
                        database=os.getenv('DB_NAME'))
    engine = create_engine(url=db_url, encoding="UTF-8")
    sm = sessionmaker(bind=engine, expire_on_commit=False)

    # bots initialization
    user_notifier = Bot(TOKEN_TELEGRAM_CLIENT, parse_mode='HTML')
    admin_notifier = Bot(TOKEN_TELEGRAM_ADMIN, parse_mode='HTML')
    # set for events in the nearest feature
    reminders = SortedSet(key=lambda x: x[1])  # stores them in format (id, reminder time)
    videoslots = SortedSet(key=lambda x: x[1])  # stores them in format (id, reminder time)

    # initial update and notifications
    update_events()
    asyncio.run(by_minute_checker())

    # scheduler initialization
    time.sleep(60 - (time.time() % 60))  # to start scheduler at the beginning of the minute
    while True:
        run_pending()
        time.sleep(1)
