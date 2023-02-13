from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import *
from sqlalchemy.engine import URL

BaseModel = declarative_base()

connection_string = URL.create("postgresql",
                               host=DB_HOST,
                               port=DB_PORT,
                               username=DB_USERNAME,
                               password=DB_PASSWORD,
                               database=DB_NAME
                               )

engine = create_engine(connection_string)

Session = sessionmaker()


class UserClient(BaseModel):
    __tablename__ = "user_client"
    tg_id = Column(Integer, primary_key=True, index=True)
    username = Column(Text)
    name = Column(Text)
    surname = Column(Text)
    created_datetime = Column(DateTime)
    state = Column(Text)


class UserAdmin(BaseModel):
    __tablename__ = "user_admin"
    tg_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    surname = Column(Text)
    email = Column(Text)
    created_datetime = Column(DateTime)
    state = Column(Text)


class Subscription(BaseModel):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user = Column(Integer, ForeignKey("user_client.tg_id"))
    type = Column(Text)
    sport_club = Column(Integer, ForeignKey("sport_club.id"))
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
    created_id = Column(Integer, ForeignKey("user_admin.tg_id"))
    telegram_group_id = Column(Text)
    telegram_group_invitation_link = Column(Text)


class BookingEvent(BaseModel):
    __tablename__ = "booking_event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_client.tg_id"))
    event_id = Column(Integer, ForeignKey("event.id"))
    booking_datetime = Column(DateTime)


class AiogramStateAdmins(BaseModel):
    __tablename__ = "aiogram_state_admins"
    user_id = Column(Integer, ForeignKey("user_admin.tg_id"), primary_key=True, index=True)
    state = Column(Text)


class AiogramDataAdmins(BaseModel):
    __tablename__ = "aiogram_data_admins"
    user_id = Column(Integer, ForeignKey("user_admin.tg_id"), primary_key=True, index=True)
    data = Column(Text)


class AiogramStateClients(BaseModel):
    __tablename__ = "aiogram_state_clients"
    user_id = Column(Integer, primary_key=True, index=True)
    state = Column(Text)


class AiogramDataClients(BaseModel):
    __tablename__ = "aiogram_data_clients"
    user_id = Column(Integer, primary_key=True, index=True)
    data = Column(Text)
