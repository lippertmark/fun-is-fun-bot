'''
файл нужно запускать каждую минуту для проверки чатов видеочатов
'''


def check_similarity(date1, date2):
    return date1.year == date2.year and date1.day == date2.day and \
           date1.month == date2.month and date1.hour == date2.hour and date1.minute == date2.minute


import datetime, pytz

from db_client.utils import get_all_time_delete

time_delete_items = get_all_time_delete()

now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
for slot in time_delete_items:
    if now.year slot.start_time.
