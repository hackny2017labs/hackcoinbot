def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def buy(user_manager, command_tokens, user_id, channel=None):
    try:
        if is_float(command_tokens[2]):
            ticker = command_tokens[1]
            shares = float(command_tokens[2])
        elif is_float(command_tokens[1]):
            ticker = command_tokens[2]
            shares = float(command_tokens[1])
        else:
            return "Not sure what you mean.  The *buy* command syntax is *buy* [ticker] [number of shares]"

        user_manager.buy_shares(ticker, shares, user_id, channel=channel)

    except Exception, e:
        print e
        return "Not sure what you mean.  The *buy* command syntax is *buy* [ticker] [number of shares]"

    return None

def sell(user_manager, command_tokens, user_id, channel=None):
    try:
        if is_float(command_tokens[2]):
            ticker = command_tokens[1]
            shares = float(command_tokens[2])
        elif is_float(command_tokens[1]):
            ticker = command_tokens[2]
            shares = float(command_tokens[1])
        else:
            return "Not sure what you mean.  The *sell* command syntax is *sell* [ticker] [number of shares]"

        user_manager.sell_shares(ticker, shares, user_id, channel=channel)

    except Exception, e:
        print e
        return "Not sure what you mean.  The *sell* command syntax is *sell* [ticker] [number of shares]"

    return None
