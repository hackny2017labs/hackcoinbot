from markets.stocks import fetch_quote


def get_price(command_tokens):
    try:
        ticker = command_tokens[0][1:]
        quote = fetch_quote(ticker)

        ticker = quote['TICKER']
        current_price = quote['PRICE']
        current_time = quote['TIME']

    except:
        return "I couldn't find the price you wanted :("

    response = "{} is currently at ${} as of {}".format(ticker, current_price, current_time)
    return response
