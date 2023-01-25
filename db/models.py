from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class UserClient(BaseModel):
    __tablename__ = "user_client"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, index=True)
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


class Subscription(BaseModel):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user = Column(Integer)
    type = Column(Text)
    sport_club = Column(Integer, ForeignKey("sport_club.id"))


class SportType(BaseModel):
    __tablename__ = "sport_type"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)


class SportClub(BaseModel):
    __tablename__ = "sport_club"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)
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


class Event(BaseModel):
    # TODO: event should be associated with club that is responsible for it
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_type = Column(Text)
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
