from utils import create_subscription_settings,create_admin_user,create_events, create_sport_clubes, create_client_user, create_sport_types
import datetime



create_client_user(338600505, 'Mark', 'Lippert', datetime.datetime.now(), '')
create_sport_types()
create_subscription_settings()
create_sport_clubes()
create_admin_user(338600505, 'Mark', 'Lippert', 'mark@lippert.com', datetime.datetime.now(), '')
create_events()

