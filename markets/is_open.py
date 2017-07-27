from datetime import datetime

def is_open(market = "stocks"):
    # note : could be made more robust

    now = datetime.now().strftime('%H%M')
    weekday = datetime.today().weekday()
    if market == "stocks":
        return '0930' <= now <= '1600' and weekday <= 4

def is_one_hour_left(market = "stocks"):
    now = datetime.now().strftime('%H%M%S')
    weekday = datetime.today().weekday()
    if market == "stocks":
        return '150000' <= now <= '150010' and weekday <= 4
