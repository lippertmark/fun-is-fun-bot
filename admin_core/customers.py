from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_
from db.models import BookingEvent, UserClient, SportClub, SubscriptionSettings, Subscription, UserAdmin
from typing import List, Any


async def get_affiliated_club(sm: sessionmaker, admin_id: int):
    """
    Gets club id  associated with admin.

    :param sm:
    :param admin_id:
    :return: club id
    """
    async with sm() as session:
        async with session.begin():
            q = select(UserAdmin.affiliated_club).where(UserAdmin.tg_id == admin_id)
            res = await session.execute(q)
            res = res.one_or_none()

    if res:
        return res.affiliated_club
    else:
        return None


async def get_event_participants(event_id: int, sm: sessionmaker) -> List[Any]:
    """
    Returns information about bookings and users for event_id.

    :param event_id:
    :param sm:
    :return:
    """
    async with sm() as session:
        async with session.begin():
            participants_r = select(UserClient, BookingEvent) \
                .where(and_(BookingEvent.event_id == event_id,
                            UserClient.tg_id == BookingEvent.user_id))
            participants = await session.execute(participants_r)

    result = [participant for participant in participants]

    return result


async def get_subscribers_tg_id(event_type: str, club_id: int, sm: sessionmaker) -> List[Any]:
    """
    Returns tg_id of users who have access to events of event_type in club.
    TODO: update this when subscription-related models will be modified

    :param event_type: "видеочат", "онлайн конференция", "оффлайн мероприятие"
    :param club_id: club holding event
    :param sm:
    :return: tg ids
    """
    if event_type == "видеочат":
        type_field = SubscriptionSettings.videochat
    elif event_type == "онлайн конференция":
        type_field = SubscriptionSettings.conference
    else:
        type_field = SubscriptionSettings.offline_event

    async with sm() as session:
        async with session.begin():
            # selecting available subscriptions id for this club
            q = select(SportClub.base_subscription, SportClub.standart_subscription, SportClub.premium_subscription) \
                .where(SportClub.id == club_id)
            subscriptions = await session.execute(q)
            subscriptions = tuple(subscriptions.all()[0])

            # selecting subscription types which include event_type
            q = select(SubscriptionSettings.subscription_type)\
                .where(and_(type_field, SubscriptionSettings.id.in_(subscriptions)))
            types = await session.execute(q)
            types = [x.subscription_type for x in types.all()]

            # selecting tg id of users
            q = select(Subscription.user)\
                .where(and_(Subscription.sport_club == club_id, Subscription.type.in_(types)))\
                .group_by(Subscription.user)
            subscribers = await session.execute(q)
            subscribers = [subscriber.user for subscriber in subscribers.fetchall()]

    return subscribers
