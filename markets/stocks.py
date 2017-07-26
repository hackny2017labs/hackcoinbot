import urllib2
import json
from datetime import datetime

def fetch_quote(ticker):
    try:
        url     = "http://finance.google.com/finance/info?client=ig&infotype=infoquoteall&q={}".format(ticker)
        u       = urllib2.urlopen(url)
        content = u.read()
        data    = json.loads(content[3:])
        info    = data[0]
        ticker  =   {
            "TICKER": info['t'],
            "PRICE": info['l'],
            "PRICEF": float(info['l']),
            "TIME": info['ltt'],
            "DATE": datetime.strptime(info['lt_dts'], "%Y-%m-%dT%H:%M:%SZ")
        }
    except Exception, e:
        return None

    return ticker

if __name__ == "__main__":
    print fetch_quote('AAPL')
