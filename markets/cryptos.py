from decimal import Decimal

import requests


COINS = {
    'btc': 'Bitcoin',
    'eth': 'Ethereum',
    'ltc': 'Litecoin',
    'bch': 'Bitcoin Cash'
}

BASE_URL = 'https://api.cryptonator.com/api/ticker/{}-usd'

def fetch_quote(symbol):
    symbol = symbol.lower()

    if symbol[-2:] in ('-c', '.c'):
        symbol = symbol[:-2]

    if symbol not in COINS:
        return None

    quote = None

    try:
        url = BASE_URL.format(symbol)
        resp = requests.get(url)
        data = resp.json()

        quote = {
            'NAME': COINS[symbol],
            'TICKER': data['ticker']['base'],
            'PRICE': Decimal(data['ticker']['price']),
            'PRICEF': Decimal(data['ticker']['price']),
            'VOLUME': Decimal(data['ticker']['volume']),
            'CHANGE_AMT': Decimal(data['ticker']['change']),
            'TIMESTAMP': data['timestamp']
        }

    except Exception as e:
        print(e)

    return quote

if __name__ == '__main__':
    print(fetch_quote('BTC'))
