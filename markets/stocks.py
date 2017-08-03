from datetime import datetime
import json
import urllib2


def fetch_quote(ticker):
    quote = None
    for exchange in ['', 'NYSEARCA:', 'NYSE:', 'NASDAQ:']:
        try:
            # try different exchanges

            url     = "http://finance.google.com/finance/info?client=ig&infotype=infoquoteall&q={}".format(exchange+ticker)
            u       = urllib2.urlopen(url)
            content = u.read()
            data    = json.loads(content[3:])
            info    = data[0]

            if "," in info['l']:
                info['l'] = info['l'].replace(',','')
            quote =   {
                "NAME": info['name'],
                "TICKER": info['t'],
                "PRICE": info['l'],
                "PRICEF": float(info['l']),
                "CHANGE": float(info['cp']),
                "CHANGE_AMT": info['c'],
                "TIME": info['ltt'],
                "DATE": datetime.strptime(info['lt_dts'], "%Y-%m-%dT%H:%M:%SZ")
            }
            break

        except Exception, e:
            print e

    return quote

if __name__ == "__main__":
    print fetch_quote('AAPL')
