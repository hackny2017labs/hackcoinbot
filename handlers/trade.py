def buy(user_object, command_tokens):
    try:
        ticker = command_tokens[1]
        shares = int(command_tokens[2])
        user_object.buy_shares(ticker, shares)
        
    except Exception, e:
        return "Not sure what you mean.  The *buy* command syntax is *buy* [ticker] [number of shares]"

    return None

def sell(user_object, command_tokens):
    try:
        ticker = command_tokens[1]
        shares = int(command_tokens[2])
        user_object.sell_shares(ticker, shares)

    except Exception, e:
        return "Not sure what you mean.  The *sell* command syntax is *sell* [ticker] [number of shares]"

    return None
