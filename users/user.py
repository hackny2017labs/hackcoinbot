from datetime import datetime
import json
import os

from slackclient import SlackClient

from markets import is_open, stocks, cryptos


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

    def get_all_tickers(self):
        tickers = set()

        for user_id in self.users:
            my_tickers = set(self.users[user_id]['positions'].keys())
            tickers = tickers.union(my_tickers)

        return list(tickers)

    def get_user_thumbnail_url(self, user_id):
        return slack_client.api_call('users.info', user=user_id)['user']['profile']['image_24']

    def check_balance(self, user_id, channel=None):
        tickers = self.users[user_id]['positions'].keys()
        stocks_tickers = [x for x in tickers if x[-2:] != '.c']
        crypto_symbols = [x for x in tickers if x[-2:] == '.c']
        quotes = stocks.batch_fetch_quotes(stocks_tickers)

        for symbol in crypto_symbols:
            quotes[symbol] = cryptos.fetch_quote(symbol)

        balance = 0
        balance += self.users[user_id]['coins']
        for ticker in tickers:
            shares = self.users[user_id]['positions'][ticker]['shares']
            stock_price = quotes[ticker]['PRICEF']
            total_value = stock_price * shares
            balance += total_value

        response = '{} has a balance of {} Hackcoins :money_with_wings:'.format(
            self.users[user_id]['first_name'],
            balance
        )

        return response

    def check_portfolio(self, user_id, channel=None):
        tickers = self.users[user_id]['positions'].keys()
        stocks_tickers = [x for x in tickers if x[-2:] != '.c']
        crypto_symbols = [x for x in tickers if x[-2:] == '.c']
        quotes = stocks.batch_fetch_quotes(stocks_tickers)

        for symbol in crypto_symbols:
            quotes[symbol] = cryptos.fetch_quote(symbol)

        response = ''

        balance = 0

        coins = self.users[user_id]['coins']
        balance += coins
        response += '{} Hackcoins :coin: \n'.format(coins)

        for ticker in tickers:
            type_text = 'shares'
            if ticker[-2:] == '.c':
                type_text = 'coins'

            shares = self.users[user_id]['positions'][ticker]['shares']
            avg_price = float(self.users[user_id]['positions'][ticker]['average_price'])

            quote = quotes[ticker]
            stock_price = quote['PRICEF']

            net_profit = (stock_price - avg_price) * shares
            balance += (stock_price * shares)

            response += '{:5} {:5} {} (buy {:04.2f} | now {:04.2f} | net profit {:04.2f})\n'.format(
                ticker,
                shares,
                type_text,
                avg_price,
                stock_price,
                net_profit
            )

        response += '\nTotal account value = {:04.2f} Hackcoins :coin: \n'.format(balance)

        return response

    def check_leaderboard(self, user_id, channel=None):
        tickers = self.get_all_tickers()
        stocks_tickers = [x for x in tickers if x[-2:] != '.c']
        crypto_symbols = [x for x in tickers if x[-2:] == '.c']
        quotes = stocks.batch_fetch_quotes(stocks_tickers)

        for symbol in crypto_symbols:
            quotes[symbol] = cryptos.fetch_quote(symbol)

        # list of tuples in the form (user_id, balance)
        balance_tuples = []

        for user_id in self.users:
            balance = 0
            balance += self.users[user_id]['coins']
            for ticker in self.users[user_id]['positions']:
                shares = self.users[user_id]['positions'][ticker]['shares']
                stock_price = quotes[ticker]['PRICEF']
                total_value = stock_price * shares
                balance += total_value
            balance = float('{:06.2f}'.format(balance))
            balance_tuples.append((user_id, balance))

        balance_tuples.sort(key=lambda x: x[1])
        balance_tuples = balance_tuples[::-1]

        response = ':racehorse: Hackcoin leaderboard :racehorse: \n'
        for i, balance in enumerate(balance_tuples):
            response += '{})\t{}\t{} '.format(i+1, self.users[balance[0]]['first_name'], balance[1])

            if i == 0:
                response += '  :100:'

            response += '\n'
        return response

    def buy_shares(self, ticker, shares, user_id, channel=None):
        try:
            is_crypto = (ticker[-2:] == '.c')
        except:
            is_crypto = False

        attachment = []
        now = datetime.now().strftime('%s')

        if is_open() or is_crypto:
            if not is_crypto:
                quote = stocks.fetch_quote(ticker)
                ticker = quote['TICKER']
                stock_price = quote['PRICEF']
                shares = int(shares)
            else:
                quote = cryptos.fetch_quote(ticker)
                ticker = ticker[:-2].upper() + '.c'
                stock_price = quote['PRICE']

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

                response = ''

                if is_crypto:
                    response_text = '{} coins of {} bought at {} each (total {} Hackcoins)'.format(
                        shares,
                        ticker,
                        stock_price,
                        total_value
                    )
                else:
                    response_text = '{} shares of {} bought at {} each (total {} coins)'.format(
                        shares,
                        ticker,
                        stock_price,
                        total_value
                    )

                average_price = self.users[user_id]['positions'][ticker]['average_price']
                cumul_pct = (stock_price - average_price) * 100.0 / average_price

                attach_color = 'good'
                if cumul_pct < 0:
                    attach_color = 'danger'

                title_text = 'Shares purchased!'
                if is_crypto:
                    title_text = 'Coins purchased!'

                attachment = [
                    {
                        'fallback': title_text,
                        'color': attach_color,
                        'author_name': self.users[user_id]['first_name'],
                        'author_icon': self.get_user_thumbnail_url(user_id),
                        'title': title_text,
                        'text': response_text,
                        'fields': [
                            {
                                'title': 'Average Buy Price',
                                'value': '{:04.2f} (overall {:04.2f}%)'.format(average_price, cumul_pct),
                                'short': False
                            },
                            {
                                'title': 'Remaining Coins',
                                'value': '{:04.2f}'.format(self.users[user_id]['coins']),
                                'short': False
                            }
                        ],
                        'ts': now
                    }
                ]
            else:
                if is_crypto:
                    shares_can_buy = int(self.users[user_id]['coins'] * 1000.0 / stock_price) / 1000.0
                else:
                    shares_can_buy = int(self.users[user_id]['coins'] * 1.0 / stock_price)

                total_can_buy = shares_can_buy * stock_price

                type_text = 'shares'
                if is_crypto:
                    type_text = 'coins'

                response = 'You can buy up to *{}* {} of {} for a total of *{}* Hackcoins  :take_my_money:'.format(
                    shares_can_buy,
                    type_text,
                    ticker,
                    total_can_buy
                )
        else:
            response = 'Markets are closed right now {} :scream:'.format(self.users[user_id]['first_name'])

        # notify their account balance
        slack_client.api_call('chat.postMessage',
                            channel=channel,
                            text=response,
                            attachments = attachment,
                            as_user=True)

        self.save_users_to_file()

    def sell_shares(self, ticker, shares, user_id, channel=None):
        try:
            is_crypto = (ticker[-2:] == '.c')
        except:
            is_crypto = False

        type_text = 'shares'
        if is_crypto:
            type_text = 'coins'

        attachment = []
        now = datetime.now().strftime('%s')

        if is_open() or is_crypto:
            if not is_crypto:
                quote = stocks.fetch_quote(ticker)
                ticker = quote['TICKER']
                stock_price = quote['PRICEF']
                shares = int(shares)
            else:
                quote = cryptos.fetch_quote(ticker)
                ticker = ticker[:-2].upper() + '.c'
                stock_price = quote['PRICE']

            total_value = stock_price * shares

            if ticker in self.users[user_id]['positions'] and shares <= self.users[user_id]['positions'][ticker]['shares']:
                # increment balance
                self.users[user_id]['coins'] += total_value

                self.users[user_id]['positions'][ticker]['shares'] -= shares

                average_price = self.users[user_id]['positions'][ticker]['average_price']
                if self.users[user_id]['positions'][ticker]['shares'] == 0:
                    del self.users[user_id]['positions'][ticker]

                response = ''

                response_text = '{} {} of {} sold at {} each (total {} coins)'.format(
                    shares,
                    type_text,
                    ticker,
                    stock_price,
                    total_value
                )

                cumul_pct = (stock_price - average_price) * 100.0 / average_price
                net_profit = shares * 1.0 * (stock_price - average_price)

                attach_color = 'good'
                if cumul_pct < 0:
                    attach_color = 'danger'

                attachment = [
                    {
                        'fallback': '{} sold!'.format(type_text.capitalize()),
                        'color': attach_color,
                        'author_name': self.users[user_id]['first_name'],
                        'author_icon': self.get_user_thumbnail_url(user_id),
                        'title': '{} sold!'.format(type_text.capitalize()),
                        'text': response_text,
                        'fields': [
                            {
                                'title': 'Average Buy Price',
                                'value': '{:04.2f}'.format(average_price),
                                'short': False
                            },
                            {
                                'title': 'Total Return',
                                'value': '{:04.2f} coins (overall {:04.2f}%)'.format(net_profit, cumul_pct),
                                'short': False
                            },
                            {
                                'title': 'Remaining Coins',
                                'value': '{:04.2f}'.format(self.users[user_id]['coins']),
                                'short': False
                            }
                        ],
                        'ts': now
                    }
                ]
            else:
                response = 'You don\'t have enough {} of {} to sell :cry:'.format(
                    type_text,
                    ticker
                )
        else:
            response = 'Markets are closed right now {} :scream:'.format(self.users[user_id]['first_name'])

        # notify their account balance
        slack_client.api_call('chat.postMessage',
                            channel=channel,
                            text=response,
                            attachments = attachment,
                            as_user=True)

        self.save_users_to_file()
