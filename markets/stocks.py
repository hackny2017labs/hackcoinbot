from datetime import datetime
import time
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

def batch_fetch_quotes(tickers):
    # Cap to 100 tickers per call (max api limit)
    TICKERS_PER_BATCH = 100

    cur = 0
    quotes = {}

    while cur < len(tickers):
        ticker_string = ",".join(tickers[cur:cur + TICKERS_PER_BATCH])
        url     = "http://finance.google.com/finance/info?client=ig&infotype=infoquoteall&q={}".format(ticker_string)
        u       = urllib2.urlopen(url)
        content = u.read()
        try:
            data    = json.loads(content[3:])
        except Exception, e:
            print e

        for info in data:
            try:
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

                ticker = info['t']

                if "." in ticker:
                    ticker = ticker.replace('.', '-')
                quotes[ticker] = quote
            except Exception, e:
                print e

        cur += TICKERS_PER_BATCH
        time.sleep(0.1)

    # handle rogue tickers that need exchange prefixes
    missing_tickers = set(tickers) - set(quotes.keys())
    for ticker in missing_tickers:
        quotes[ticker] = fetch_quote(ticker)

    return quotes

if __name__ == "__main__":
    print fetch_quote('AAPL')
