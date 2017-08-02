from datetime import datetime
import json
import os

from slackclient import SlackClient

from markets import is_open, stocks
import redis_interface


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
            shares = self.users[user_id]['positions'][ticker]['shares']
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

        balance = 0

        coins = self.users[user_id]['coins']
        balance += coins
        response += "{} Hackcoins :coin: \n".format(coins)

        for ticker in self.users[user_id]['positions']:
            shares = self.users[user_id]['positions'][ticker]['shares']
            avg_price = float(self.users[user_id]['positions'][ticker]['average_price'])

            quote = stocks.fetch_quote(ticker)
            stock_price = quote['PRICEF']

            day_change = quote['CHANGE']
            day_change_str = ""
            if day_change > 0:
                day_change_str = ":arrow_up_small: {:04.2f}%".format(abs(day_change))
            elif day_change < 0:
                day_change_str = ":arrow_down_small: {:04.2f}%".format(abs(day_change))
            else:
                day_change_str = ":zero:%"

            net_profit = (stock_price - avg_price) * shares
            balance += (stock_price * shares)

            response += "{:5} {:5} shares (buy {:04.2f} | now {:04.2f} | net profit {:04.2f})\n".format(
                ticker,
                shares,
                avg_price,
                stock_price,
                net_profit
            )

        response += "\nTotal account value = {:04.2f} Hackcoins :coin: \n".format(balance)

        return response

    def check_leaderboard(self, user_id, channel=None):
        # list of tuples in the form (user_id, balance)
        balance_tuples = []


        for user_id in self.users:
            balance = 0
            balance += self.users[user_id]['coins']
            for ticker in self.users[user_id]['positions']:
                shares = self.users[user_id]['positions'][ticker]['shares']
                stock_price = stocks.fetch_quote(ticker)['PRICEF']
                total_value = stock_price * shares
                balance += total_value
            balance_tuples.append((user_id, balance))

        balance_tuples.sort(key=lambda x: x[1])
        balance_tuples = balance_tuples[::-1]

        response = ":racehorse: Hackcoin leaderboard :racehorse: \n"
        for i, balance in enumerate(balance_tuples):
            response += "{})\t{}\t{} ".format(i+1, self.users[balance[0]]['first_name'], balance[1])

            if i == 0:
                response += "  :100:"

            response += "\n"
        return response

    def buy_shares(self, ticker, shares, user_id, channel=None):

        attachment = []
        now = datetime.now().strftime('%s')

        if is_open():
            quote = stocks.fetch_quote(ticker)
            ticker = quote['TICKER']
            stock_price = quote['PRICEF']
            total_value = stock_price * shares

            if total_value < self.users[user_id]['coins']:
                # decrement balance
                self.users[user_id]['coins'] -= total_value

                # increment share ct, adjust the average buy price
                if ticker in self.users[user_id]['positions']:
                    old_price = self.users[user_id]['positions'][ticker]['average_price']
                    old_shares = self.users[user_id]['positions'][ticker]['shares']
                    old_total = float(old_price) * float(old_shares)
                    new_total = old_total + total_value
                    new_shares = old_shares + shares
                    new_price = new_total * 1.0 / new_shares

                    self.users[user_id]['positions'][ticker]['shares'] += shares
                    self.users[user_id]['positions'][ticker]['average_price'] = new_price
                else:
                    self.users[user_id]['positions'][ticker] = {}
                    self.users[user_id]['positions'][ticker]['shares'] = shares
                    self.users[user_id]['positions'][ticker]['average_price'] = stock_price

                response = ""

                response_text = '{} shares of {} bought at {} each (total {} coins)'.format(
                    shares,
                    ticker,
                    stock_price,
                    total_value
                )

                average_price = self.users[user_id]['positions'][ticker]['average_price']
                cumul_pct = (stock_price - average_price) * 100.0 / average_price

                attach_color = "good"
                if cumul_pct < 0:
                    attach_color = "danger"

                attachment = [
                    {
                        "fallback": "Shares purchased!",
                        "color": attach_color,
                        "author_name": self.users[user_id]['first_name'],
                        "author_icon": self.get_user_thumbnail_url(user_id),
                        "title": "Shares purchased!",
                        "text": response_text,
                        "fields": [
                            {
                                "title": "Average Buy Price",
                                "value": "{:04.2f} (overall {:04.2f}%)".format(average_price, cumul_pct),
                                "short": False
                            },
                            {
                                "title": "Remaining Coins",
                                "value": "{:04.2f}".format(self.users[user_id]['coins']),
                                "short": False
                            }
                        ],
                        "ts": now
                    }
                ]
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
                            attachments = attachment,
                            as_user=True)

        self.save_users_to_file()

    def sell_shares(self, ticker, shares, user_id, channel=None):

        attachment = []
        now = datetime.now().strftime('%s')

        if is_open():
            quote = stocks.fetch_quote(ticker)
            ticker = quote['TICKER']
            stock_price = quote['PRICEF']
            total_value = stock_price * shares

            if ticker in self.users[user_id]['positions'] and shares <= self.users[user_id]['positions'][ticker]['shares']:
                # increment balance
                self.users[user_id]['coins'] += total_value

                self.users[user_id]['positions'][ticker]['shares'] -= shares

                average_price = self.users[user_id]['positions'][ticker]['average_price']
                if self.users[user_id]['positions'][ticker]['shares'] == 0:
                    del self.users[user_id]['positions'][ticker]

                response = ""

                response_text = '{} shares of {} sold at {} each (total {} coins)'.format(
                    shares,
                    ticker,
                    stock_price,
                    total_value
                )

                cumul_pct = (stock_price - average_price) * 100.0 / average_price
                net_profit = shares * 1.0 * (stock_price - average_price)

                attach_color = "good"
                if cumul_pct < 0:
                    attach_color = "danger"

                attachment = [
                    {
                        "fallback": "Shares sold!",
                        "color": attach_color,
                        "author_name": self.users[user_id]['first_name'],
                        "author_icon": self.get_user_thumbnail_url(user_id),
                        "title": "Shares sold!",
                        "text": response_text,
                        "fields": [
                            {
                                "title": "Average Buy Price",
                                "value": "{:04.2f}".format(average_price),
                                "short": False
                            },
                            {
                                "title": "Total Return",
                                "value": "{:04.2f} coins (overall {:04.2f}%)".format(net_profit, cumul_pct),
                                "short": False
                            },
                            {
                                "title": "Remaining Coins",
                                "value": "{:04.2f}".format(self.users[user_id]['coins']),
                                "short": False
                            }
                        ],
                        "ts": now
                    }
                ]
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
                            attachments = attachment,
                            as_user=True)

        self.save_users_to_file()
