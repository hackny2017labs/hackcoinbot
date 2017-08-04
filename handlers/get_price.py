from datetime import datetime

from markets import stocks, cryptos

def get_price(command_tokens):
    if '-c' in command_tokens or \
        command_tokens[0][-2:] in set(['-c', '.c']):
        return get_crpyto_price(command_tokens)

    try:
        ticker = command_tokens[0][1:]
        quote = stocks.fetch_quote(ticker)
        if quote == None:
            raise Exception('no quote found')
    except:
        return 'I couldn't find the price you wanted :cry:', None

    title = '{} ({})'.format(
        quote['NAME'],
        quote['TICKER']
    )

    bar_color = 'good'
    try:
        if float(quote['CHANGE_AMT']) < 0:
            bar_color = 'danger'
    except:
        pass

    chart_url = 'http://finviz.com/chart.ashx?t={}&ty=c&ta=1&p=d&s=l'.format(
        quote['TICKER']
    )

    change_text = '{} ({}%)'.format(
        quote['CHANGE_AMT'],
        quote['CHANGE']
    )

    now = datetime.now().strftime('%s')

    attachment = [
       {
           'fallback': 'Check Price',
           'color': bar_color,
           'title': title,
           'fields': [
                {
                    'title': 'Price',
                    'value': quote['PRICE'],
                    'short': True
                },
                {
                    'title': 'Change',
                    'value': change_text,
                    'short': True
                }
            ],
           'image_url': chart_url,
           'footer': 'Google Finance | Finviz',
           'ts': now
       }
    ]

    return '', attachment

def get_crpyto_price(command_tokens):
    try:
        symbol = command_tokens[0][1:]
        quote = cryptos.fetch_quote(symbol)
        if quote == None:
            raise Exception('no quote found')
    except:
        return 'We don't support that coin yet :cry:', None

    title = '{} ({})'.format(
        quote['NAME'],
        quote['TICKER']
    )

    bar_color = 'good'
    try:
        if quote['CHANGE_AMT'] < 0:
            bar_color = 'danger'
    except:
        pass

    change_pct = quote['CHANGE_AMT'] * 100.0 / (quote['PRICE'] - quote['CHANGE_AMT'])
    change_text = '{:04.3f} ({:04.3f}%)'.format(
        quote['CHANGE_AMT'],
        change_pct
    )

    attachment = [
       {
           'fallback': 'Check Price',
           'color': bar_color,
           'title': title,
           'fields': [
                {
                    'title': 'Price',
                    'value': '{:05.3f}'.format(quote['PRICE']),
                    'short': True
                },
                {
                    'title': 'Change (1hr)',
                    'value': change_text,
                    'short': True
                },
                {
                    'title': 'Volume (24hr)',
                    'value': '{:05.3f}'.format(quote['VOLUME']),
                    'short': True
                },
            ],
           'footer': 'Google Finance | Finviz',
           'ts': quote['TIMESTAMP']
       }
    ]

    return '', attachment
