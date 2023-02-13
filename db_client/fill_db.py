from db_client.models import *
import datetime


def create_sport_types():
    local_session = Session(bind=engine)
    football = SportType(name='Футбол')
    hockey = SportType(name='Хоккей')
    basketball = SportType(name='Баскетбол')
    volleyball = SportType(name='Волейбол')
    local_session.add(football)
    local_session.add(hockey)
    local_session.add(basketball)
    local_session.add(volleyball)
    local_session.commit()


def create_subscription_settings():
    local_session = Session(bind=engine)
    base = SubscriptionSettings(subscription_type='Базовая', videochat=True, conference=False, offline_event=False,
                                price=150)
    standard = SubscriptionSettings(subscription_type='Стандарт', videochat=True, conference=True, offline_event=False,
                                    price=500)
    premium = SubscriptionSettings(subscription_type='Премиум', videochat=True, conference=True, offline_event=True,
                                   price=2000)
    local_session.add(base)
    local_session.add(standard)
    local_session.add(premium)
    local_session.commit()


def create_sport_clubs():
    local_session = Session(bind=engine)

    f2 = SportClub(name='Ак барс', description="Ак барс — российский хоккейный клуб, выступающий в Континентальной "
                                               "хоккейной лиге. Базируется в городе Казань. Основан в 1956 году под "
                                               "названием «Машстрой», в 1958 году изменил название на «СК имени "
                                               "Урицкого», под которым выступал до 1990 года. В 1990—1995 годах"
                                               " назывался «Итиль».\n\n\n🏆Единственный трёхкратный обладатель "
                                               "Кубка Гагарина\n\n🏆Двухкратные обладатели кубка европейских "
                                               "чемпионов\n\n🏆Пятикратные чемпионы России",
                   photo="AgACAgIAAxkBAAIir2PqGtWhFpvep3x99vdlbobnTMPxAAJSyjEbeTFRSx6mQJds4CwvAQADAgADcwADLgQ", sport_type=2,
                   base_subscription=1, standart_subscription=2, premium_subscription=3)
    f3 = SportClub(name='Зенит', description="Зенит — российский мужской волейбольный клуб из Казани. Основан в 2000 "
                                             "году; до 2004 года назывался «Динамо», с 2005 по июнь 2008 года — "
                                             "«Динамо-Таттрансгаз».\n\n\n🏆Десятикратный чемпион России\n\n"
                                             "🏆Одиннадцатикратный обладатель Кубка России\n\n🏆 Шестикратный "
                                             "победитель Лиги чемпионов\n\n🏆Победитель клубного чемпионата мира 2017.",
                   photo="AgACAgIAAxkBAAIisWPqGv-Qht54r1xFWKPS2pXhnyIKAAJTyjEbeTFRS9pcO5OjZM5EAQADAgADcwADLgQ", sport_type=4,
                   base_subscription=1, standart_subscription=2, premium_subscription=3)
    f4 = SportClub(name='УНИКС', description="УНИКС — российский баскетбольный клуб из Казани. Выступает в Единой лиге"
                                             " ВТБ. УНИКС — аббревиатура от «Университет — Культура — Спорт»\n\n\n"
                                             "🏆Трёхкратные обладатели Кубка России\n\n🏆 Обладатели Еврокубка\n\n"
                                             "🏆 Чемпионы Лиги Европы ФИБА🏆"
                                             " Чемпионы Североевропейской баскетбольная лига",
                    photo="AgACAgIAAxkBAAIis2PqGysQHxG-IZgQ_W9kk7smVJptAAJVyjEbeTFRSykYB2IL5Yc7AQADAgADcwADLgQ", sport_type=3,
                   base_subscription=1, standart_subscription=2, premium_subscription=3)
    f5 = SportClub(name='Рубин', description="Руби́н — российский профессиональный футбольный клуб из города Казани."
                                             " Основан 20 апреля 1958 года под названием «Искра» как команда Казанского"
                                             " авиационного завода No 22 имени С. П. Горбунова.\n\n\n🏆"
                                             " Двукратный чемпион России\n\n🏆 Обладатель Кубка России\n\n"
                                             "🏆 Обладатель Кубка Содружества\n\n🏆 Обладатель Суперкубка России",
                   photo="AgACAgIAAxkBAAIitWPqG0EGxxIR6rRvDKoL_21NbVRwAAJWyjEbeTFRS404Czs-zyhJAQADAgADcwADLgQ", sport_type=1,
                   base_subscription=1, standart_subscription=2, premium_subscription=3)
    # local_session.add(f2)
    # local_session.add(f3)
    # local_session.add(f4)
    local_session.add(f5)
    local_session.commit()


def create_admin_user(tg_id, name, surname, email, created_datetime, state=''):
    local_session = Session(bind=engine)

    new_user = UserAdmin(tg_id=tg_id, name=name, surname=surname, email=email, created_datetime=created_datetime,
                         state=state)
    local_session.add(new_user)
    local_session.commit()


# def create_events(club):
#     local_session = Session(bind=engine)
#     event_1 = Event(event_type='Оффлайн мероприятие', club=club, name='первый', tg_alias='lippert_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=15,
#                     created_datetime=datetime.datetime.now(), created_id=338600505, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     event_2 = Event(event_type='Оффлайн мероприятие', club=club, name='Второй', tg_alias='lippert_ne_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=1000,
#                     created_datetime=datetime.datetime.now(), created_id=338600505, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     event_3 = Event(event_type='Оффлайн мероприятие', club=club, name='Третий!', tg_alias='lippert_ne_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=5,
#                     created_datetime=datetime.datetime.now(), created_id=338600505, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     event_4 = Event(event_type='Оффлайн мероприятие', club=club, name='Четвертый', tg_alias='lippert_mark',
#                     start_datetime=datetime.datetime.now(), duration=120, max_amount_of_people=30,
#                     created_datetime=datetime.datetime.now(), created_id=338600505, telegram_group_id='123',
#                     telegram_group_invitation_link='12312')
#     local_session.add(event_1)
#     local_session.add(event_2)
#     local_session.add(event_3)
#     local_session.add(event_4)
#     local_session.commit()


# create_sport_types()
#
#
# create_subscription_settings()

# create_sport_clubs()

# create_admin_user(542643041, 'Zaitun', 'admin', 'zaitun@zaitun.com', datetime.datetime.now())
