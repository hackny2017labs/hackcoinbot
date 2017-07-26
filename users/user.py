from slackclient import SlackClient
from markets import is_open, stocks
import os

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# temp: dumb dictionary for now, later connect to DB
global_users = {}

INITIAL_COINS = 10000

class HackcoinUser(object):
    def __init__(self, user_id, channel=None):
        self.user = {}
        self.channel = channel

        if user_id not in global_users:
            profile = slack_client.api_call('users.info', user=user_id)['user']['profile']
            global_users[user_id] = {
                'first_name': profile['first_name'],
                'last_name': profile['last_name'],
                'real_name': profile['real_name'],
                'coins': INITIAL_COINS,
                'positions': {}
            }

            response = 'Welcome {} :wave: You will start off with {} HackCoins :coin: '.format(profile['first_name'], INITIAL_COINS)
            # notify their account balance
            slack_client.api_call('chat.postMessage', channel=channel,
                                  text=response,
                                  as_user=True)

        self.user = global_users[user_id]

    def buy_shares(self, ticker, shares):
        if is_open():
            quote = stocks.fetch_quote(ticker)
            ticker = quote['TICKER']
            stock_price = quote['PRICEF']
            total_value = stock_price * shares

            if total_value < self.user['coins']:
                # decrement balance
                self.user['coins'] -= total_value

                # increment share ct
                if ticker in self.user['positions']:
                    self.user['positions'][ticker] += shares
                else:
                    self.user['positions'][ticker] = shares

                response = '{} bought {} shares of {} :joy: \n{} has {} coins left :doge:'.format(
                    self.user["first_name"],
                    shares,
                    ticker,
                    self.user["first_name"],
                    self.user["coins"]
                )
            else:
                response = 'You only have {} coins but you need {} coins to buy {} shares of {} :cry:'.format(
                    self.user['coins'],
                    total_value,
                    shares,
                    ticker
                )
        else:
            response = 'Markets are closed right now {} :scream:'.format(self.user["first_name"])

        # notify their account balance
        slack_client.api_call('chat.postMessage',
                            channel=self.channel,
                            text=response,
                            as_user=True)

    def sell_shares(self, ticker, shares):
        if is_open():
            quote = stocks.fetch_quote(ticker)
            ticker = quote['TICKER']
            stock_price = quote['PRICEF']
            total_value = stock_price * shares

            if ticker in self.user['positions'] and shares <= self.user['positions'][ticker]:
                # decrement balance
                self.user['coins'] += total_value

                self.user['positions'][ticker] -= shares
                if self.user['positions'][ticker] == 0:
                    del self.user['positions'][ticker]

                response = '{} sold {} shares of {} :joy: \n{} now has {} coins :doge:'.format(
                    self.user["first_name"],
                    shares,
                    ticker,
                    self.user["first_name"],
                    self.user["coins"]
                )
            else:
                response = 'You don\'t have enough shares of {} to sell :cry:'.format(
                    ticker
                )
        else:
            response = 'Markets are closed right now {} :scream:'.format(self.user["first_name"])

        # notify their account balance
        slack_client.api_call('chat.postMessage',
                            channel=self.channel,
                            text=response,
                            as_user=True)
