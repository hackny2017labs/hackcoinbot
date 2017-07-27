from slackclient import SlackClient
from markets import is_open, stocks
import os
import json

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# json file
USER_JSON = 'user_data.json'
INITIAL_COINS = 10000

class HackcoinUserManager(object):
    def __init__(self):
        self.users = {}
        self.load_users_from_file()

    def load_user(self, user_id, channel=None):
        if user_id not in self.users:
            profile = slack_client.api_call('users.info', user=user_id)['user']['profile']
            self.users[user_id] = {
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
        self.save_users_to_file()

    def load_users_from_file(self):
        with open(USER_JSON, 'r') as f:
            self.users = json.load(f)

    def save_users_to_file(self):
        with open(USER_JSON, 'w') as f:
            json.dump(self.users, f)

    def get_user_thumbnail_url(self, user_id):
        return slack_client.api_call('users.info', user=user_id)['user']['profile']['image_24']

    def check_balance(self, user_id, channel=None):
        balance = 0
        balance += self.users[user_id]['coins']
        for ticker in self.users[user_id]['positions']:
            shares = self.users[user_id]['positions'][ticker]
            stock_price = stocks.fetch_quote(ticker)['PRICEF']
            total_value = stock_price * shares
            balance += total_value

        response = '{} has a balance of {} Hackcoins :money_with_wings:'.format(
            self.users[user_id]["first_name"],
            balance
        )

        return response

    def check_portfolio(self, user_id, channel=None):
        response = ""

        coins = self.users[user_id]['coins']
        response += "{} Hackcoins :coin: \n".format(coins)

        for ticker in self.users[user_id]['positions']:
            shares = self.users[user_id]['positions'][ticker]
            quote = stocks.fetch_quote(ticker)
            stock_price = quote['PRICEF']
            day_change = quote['CHANGE']
            total_value = stock_price * shares

            if day_change < 0:
                response += "{:7} shares of {:5}\t :arrow_up_small: {:04.2f}% today\t worth {} Hackcoins\n".format(shares, ticker, abs(day_change), total_value)
            elif day_change > 0:
                response += "{:7} shares of {:5}\t :arrow_down_small: {:04.2f}% today\t worth {} Hackcoins\n".format(shares, ticker, abs(day_change), total_value)
            else:
                response += "{:7} shares of {:5}\t :zero:% today\t| worth {} Hackcoins\n".format(shares, ticker, abs(day_change), total_value)

        return response

    def check_leaderboard(self, user_id, channel=None):
        # list of tuples in the form (user_id, balance)
        balance_tuples = []

        for user_id in self.users:
            balance = 0
            balance += self.users[user_id]['coins']
            for ticker in self.users[user_id]['positions']:
                shares = self.users[user_id]['positions'][ticker]
                stock_price = stocks.fetch_quote(ticker)['PRICEF']
                total_value = stock_price * shares
                balance += total_value
            balance_tuples.append((user_id, balance))

        balance_tuples.sort(key=lambda x: x[1])
        balance_tuples = balance_tuples[::-1]

        response = "Hackcoin leaderboard :racehorse: \n"
        for i, balance in enumerate(balance_tuples):
            response += "{})\t{}\t{} coins".format(i+1, self.users[balance[0]]['first_name'], balance[1])

            if i == 0:
                response += "  :100:"

            response += "\n"
        return response

    def buy_shares(self, ticker, shares, user_id, channel=None):
        if is_open():
            quote = stocks.fetch_quote(ticker)
            ticker = quote['TICKER']
            stock_price = quote['PRICEF']
            total_value = stock_price * shares

            if total_value < self.users[user_id]['coins']:
                # decrement balance
                self.users[user_id]['coins'] -= total_value

                # increment share ct
                if ticker in self.users[user_id]['positions']:
                    self.users[user_id]['positions'][ticker] += shares
                else:
                    self.users[user_id]['positions'][ticker] = shares

                response = '{} bought {} shares of {} :joy: \n{} has {} coins left :doge:'.format(
                    self.users[user_id]["first_name"],
                    shares,
                    ticker,
                    self.users[user_id]["first_name"],
                    self.users[user_id]["coins"]
                )
            else:
                response = 'You only have {} coins but you need {} coins to buy {} shares of {} :cry:'.format(
                    self.users[user_id]['coins'],
                    total_value,
                    shares,
                    ticker
                )
        else:
            response = 'Markets are closed right now {} :scream:'.format(self.users[user_id]["first_name"])

        # notify their account balance
        slack_client.api_call('chat.postMessage',
                            channel=channel,
                            text=response,
                            as_user=True)

        self.save_users_to_file()

    def sell_shares(self, ticker, shares, user_id, channel=None):
        if is_open():
            quote = stocks.fetch_quote(ticker)
            ticker = quote['TICKER']
            stock_price = quote['PRICEF']
            total_value = stock_price * shares

            if ticker in self.users[user_id]['positions'] and shares <= self.users[user_id]['positions'][ticker]:
                # decrement balance
                self.users[user_id]['coins'] += total_value

                self.users[user_id]['positions'][ticker] -= shares
                if self.users[user_id]['positions'][ticker] == 0:
                    del self.users[user_id]['positions'][ticker]

                response = '{} sold {} shares of {} :joy: \n{} now has {} coins :doge:'.format(
                    self.users[user_id]["first_name"],
                    shares,
                    ticker,
                    self.users[user_id]["first_name"],
                    self.users[user_id]["coins"]
                )
            else:
                response = 'You don\'t have enough shares of {} to sell :cry:'.format(
                    ticker
                )
        else:
            response = 'Markets are closed right now {} :scream:'.format(self.users[user_id]["first_name"])

        # notify their account balance
        slack_client.api_call('chat.postMessage',
                            channel=channel,
                            text=response,
                            as_user=True)

        self.save_users_to_file()
