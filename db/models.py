from sqlalchemy import Column, Integer, BigInteger, Text, DateTime, Boolean, ForeignKey, Time
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class UserClient(BaseModel):
    __tablename__ = "user_client"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, index=True)
    username = Column(Text)
    name = Column(Text)
    surname = Column(Text)
    created_datetime = Column(DateTime)


class UserAdmin(BaseModel):
    __tablename__ = "user_admin"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, index=True)
    name = Column(Text)
    surname = Column(Text)
    email = Column(Text)
    created_datetime = Column(DateTime)
    affiliated_club = Column(Integer)


class Subscription(BaseModel):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user = Column(Integer)
    type = Column(Text)
    sport_club = Column(Integer, ForeignKey("sport_club.id"))
    sub_settings = Column(Integer, ForeignKey("subscription_settings.id"))
    expired_date = Column(DateTime)


class SportType(BaseModel):
    __tablename__ = "sport_type"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)


class SportClub(BaseModel):
    __tablename__ = "sport_club"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)
    description = Column(Text)
    photo = Column(Text)
    sport_type = Column(Integer, ForeignKey("sport_type.id"), index=True)
    base_subscription = Column(Integer, ForeignKey("subscription_settings.id"))
    standart_subscription = Column(Integer, ForeignKey("subscription_settings.id"))
    premium_subscription = Column(Integer, ForeignKey("subscription_settings.id"))


class SubscriptionSettings(BaseModel):
    __tablename__ = "subscription_settings"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    subscription_type = Column(Text)
    videochat = Column(Boolean)
    conference = Column(Boolean)
    offline_event = Column(Boolean)
    price = Column(Integer)


class Event(BaseModel):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_type = Column(Text)
    club = Column(Integer, ForeignKey("sport_club.id"))
    name = Column(Text)
    tg_alias = Column(Text)
    start_datetime = Column(DateTime)
    duration = Column(Integer)
    max_amount_of_people = Column(Integer)
    created_datetime = Column(DateTime)
    created_id = Column(Integer)
    telegram_group_id = Column(Text)
    telegram_group_invitation_link = Column(Text)


class BookingEvent(BaseModel):
    __tablename__ = "booking_event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    event_id = Column(Integer, ForeignKey("event.id"))
    booking_datetime = Column(DateTime)
    slot_id = Column(Integer)


class AiogramStateAdmins(BaseModel):
    __tablename__ = "aiogram_state_admins"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    state = Column(Text)


class AiogramDataAdmins(BaseModel):
    __tablename__ = "aiogram_data_admins"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    data = Column(Text)


class AiogramStateClients(BaseModel):
    __tablename__ = "aiogram_state_clients"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    state = Column(Text)


class AiogramDataClients(BaseModel):
    __tablename__ = "aiogram_data_clients"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    data = Column(Text)


class Chat(BaseModel):
    __tablename__ = "chat"
    chat_id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    event = Column(Integer, default=0)  # 0 - если ни к кому не принадлежит


class LinkForUserToChat(BaseModel):
    __tablename__ = "link_for_user_to_chat"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    user_id = Column(Integer)
    link = Column(Text)
    date_expired = Column(DateTime(timezone=True))


class Slots(BaseModel):
    __tablename__ = "slots_for_videochat"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=0)
    event_id = Column(Integer, ForeignKey("event.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)