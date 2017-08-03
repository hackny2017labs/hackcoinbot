from datetime import datetime

from markets.stocks import fetch_quote

def get_price(command_tokens):
    try:
        ticker = command_tokens[0][1:]
        quote = fetch_quote(ticker)
    except:
        return "I couldn't find the price you wanted :cry:"

    title = "{} ({})".format(
        quote['NAME'],
        quote['TICKER']
    )

    chart_url = "http://finviz.com/chart.ashx?t={}&ty=c&ta=1&p=d&s=l".format(
        quote['TICKER']
    )

    change_text = "{} ({}%)".format(
        quote['CHANGE_AMT'],
        quote['CHANGE']
    )

    now = datetime.now().strftime('%s')

    attachment = [
       {
           "fallback": "Check Price",
           "color": "good",
           "title": title,
           "fields": [
                {
                    "title": "Price",
                    "value": quote['PRICE'],
                    "short": True
                },
                {
                    "title": "Change",
                    "value": change_text,
                    "short": True
                }
            ],
           "image_url": chart_url,
           "footer": "Google Finance | Finviz",
           "ts": now
       }
    ]

    return "", attachment
