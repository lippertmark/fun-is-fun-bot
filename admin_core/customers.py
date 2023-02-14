from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_
from db.models import BookingEvent, UserClient
from typing import List, Any


async def get_event_participants(event_id: int, sm: sessionmaker) -> List[Any]:
    """
    Returns information about bookings and users for event_id.

    :param event_id:
    :param sm:
    :return:
    """
    async with sm() as session:
        async with session.begin():
            participants_r = select(UserClient, BookingEvent)\
                .where(and_(BookingEvent.event_id == event_id,
                            UserClient.tg_id == BookingEvent.user_id))
            participants = await session.execute(participants_r)

    result = [participant for participant in participants]

    return result
