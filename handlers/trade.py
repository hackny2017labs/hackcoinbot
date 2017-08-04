from utils import coerce_decimal


def buy(user_manager, command_tokens, user_id, channel=None):
    try:
        val = coerce_decimal(command_tokens[2])

        if not val is None:
            ticker = command_tokens[1]
            shares = val
        else:
            return 'Not sure what you mean.  The *buy* command syntax is *buy* [ticker] [number of shares]'

        user_manager.buy_shares(ticker, shares, user_id, channel=channel)

    except Exception, e:
        print(e)
        return 'Not sure what you mean.  The *buy* command syntax is *buy* [ticker] [number of shares]'

    return None

def sell(user_manager, command_tokens, user_id, channel=None):
    try:
        val = coerce_decimal(command_tokens[2])
        if not val is None:
            ticker = command_tokens[1]
            shares = val
        else:
            return 'Not sure what you mean.  The *sell* command syntax is *sell* [ticker] [number of shares]'

        user_manager.sell_shares(ticker, shares, user_id, channel=channel)

    except Exception, e:
        print(e)
        return 'Not sure what you mean.  The *sell* command syntax is *sell* [ticker] [number of shares]'

    return None
