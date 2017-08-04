from datetime import datetime
from decimal import Decimal
import time
import json


BASE_URL = 'http://finance.google.com/finance/info?client=ig&infotype=infoquoteall&q={}'
TICKERS_PER_BATCH = 100

def fetch_quote(ticker):
    quote = None
    for exchange in ['', 'NYSEARCA:', 'NYSE:', 'NASDAQ:']:
        try:
            # try different exchanges

            url = BASE_URL.format(exchange + ticker)
            resp = requests.get(url)
            data = json.loads(resp.text[3:])
            info = data[0]

            if ',' in info['l']:
                info['l'] = info['l'].replace(',', '')

            quote = {
                'NAME': info['name'],
                'TICKER': info['t'],
                'PRICE': info['l'],
                'PRICEF': Decimal(info['l']),
                'CHANGE': Decimal(info['cp']),
                'CHANGE_AMT': info['c'],
                'TIME': info['ltt'],
                'DATE': datetime.strptime(info['lt_dts'], '%Y-%m-%dT%H:%M:%SZ')
            }

            break

        except Exception as e:
            print(e)

    return quote

def batch_fetch_quotes(tickers):
    # Cap to 100 tickers per call (max api limit)

    cur = 0
    quotes = {}

    while cur < len(tickers):
        ticker_string = ','.join(tickers[cur:cur + TICKERS_PER_BATCH])
        url = BASE_URL.format(ticker_string)
        resp = requests.get(url)

        try:
            data = json.loads(resp.text[3:])
        except Exception, e:
            print(e)

        for info in data:
            try:
                if ',' in info['l']:
                    info['l'] = info['l'].replace(',', '')

                quote = {
                    'NAME': info['name'],
                    'TICKER': info['t'],
                    'PRICE': info['l'],
                    'PRICEF': Decimal(info['l']),
                    'CHANGE': Decimal(info['cp']),
                    'CHANGE_AMT': info['c'],
                    'TIME': info['ltt'],
                    'DATE': datetime.strptime(info['lt_dts'], '%Y-%m-%dT%H:%M:%SZ')
                }

                ticker = info['t']

                if '.' in ticker:
                    ticker = ticker.replace('.', '-')

                quotes[ticker] = quote
            except Exception as e:
                print(e)

        cur += TICKERS_PER_BATCH
        time.sleep(0.1)

    # handle rogue tickers that need exchange prefixes
    missing_tickers = set(tickers) - set(quotes.keys())
    for ticker in missing_tickers:
        quotes[ticker] = fetch_quote(ticker)

    return quotes

if __name__ == '__main__':
    print(fetch_quote('AAPL'))
