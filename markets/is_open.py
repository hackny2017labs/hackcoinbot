from datetime import datetime

def is_open(market = "stocks"):
    # note : could be made more robust

    now = datetime.now().strftime('%H%M')
    weekday = datetime.today().weekday()
    if market == "stocks":
        return '0930' <= now <= '1600' and weekday <= 4
