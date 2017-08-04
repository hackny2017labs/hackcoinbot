from datetime import datetime, time


def is_open(market='stocks'):
    now = datetime.now()
    weekday = now.weekday()
    a = time(hour=9, minute=30)
    b = time(hour=16)

    if market == 'stocks':
        return a <= now.time() <= b and weekday <= 4
    else:
        return True

def is_one_hour_left(market='stocks'):
    now = datetime.now()
    weekday = now.weekday()
    a = datetime(year=now.year, month=now.month, day=now.day, hour=15)
    b = datetime(year=now.year, month=now.month, day=now.day, hour=15, minute=1)

    if market == 'stocks':
        return a <= now <= b and weekday <= 4
    else:
        return True
