def print_help():
    return """
Hackcoin is a trading and investment currency for slack.  Everyone starts with 10000 Hackcoins.
You can message @hackcoinbot to access your Hackcoins.

Check Account:
-------------
@hackcoinbot: balance
@hackcoinbot: [*p*]ortfolio

Trading:
-------
Trade shares of stock with Hackcoin! 1 coin = 1 USD.
Buy and sell using a ticker and share count.

@hackcoinbot: $AAPL         check price of Apple
@hackcoinbot: buy AAPL 10   [*b*]uy 10 shares of Apple
@hackcoinbot: sell MSFT 10  [*s*]ell 10 shares of Microsoft

Several cryptocurrencies are also supported with the suffix '.c':
@hackcoinbot: $BTC.c         check price of Bitcoin
@hackcoinbot: buy ETH.c 1.5  [*b*]uy 1.5 coins of Ethereum

Leaderboard:
-----------
@hackcoinbot: [*l*]eaderboard

Shitpost:
--------
:wink: you already know
    """
