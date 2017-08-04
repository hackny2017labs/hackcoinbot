from datetime import datetime
import time
import json
import urllib2
import requests

coins = {
    'btc': 'Bitcoin',
    'eth': 'Ethereum',
    'ltc': 'Litecoin',
    'bch': 'Bitcoin Cash'
}

def fetch_quote(symbol):
    symbol = symbol.lower()
    if symbol[-2:] in set(['-c', '.c']):
        symbol = symbol[:-2]
    if symbol not in coins.keys():
        return None

    quote = None

    try:
        url = 'https://api.cryptonator.com/api/ticker/{}-usd'.format(symbol)
        u = urllib2.urlopen(url)
        content = u.read()
        data = json.loads(content)

        quote = {
            'NAME': coins[symbol],
            'TICKER': data['ticker']['base'],
            'PRICE': float(data['ticker']['price']),
            'PRICEF': float(data['ticker']['price']),
            'VOLUME': float(data['ticker']['volume']),
            'CHANGE_AMT': float(data['ticker']['change']),
            'TIMESTAMP': data['timestamp']
        }

    except Exception, e:
        print(e)

    return quote

if __name__ == '__main__':
    print(fetch_quote('BTC'))
