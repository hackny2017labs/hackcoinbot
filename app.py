import os
from datetime import datetime
import time
import random

from slackclient import SlackClient

from handlers import is_private_message, get_price, get_command_type, buy, sell, portfolio, print_help
from markets import is_one_hour_left
from users import HackcoinUserManager


# env variable bot_id
BOT_ID = os.environ.get('SLACK_BOT_ID')

# constants
AT_BOT = '<@{}>'.format(BOT_ID)

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# users manager object
user_manager = HackcoinUserManager()

def handle_command(command, channel, user_id):
    '''
    Receives commands directed at the bot and determines if they
    are valid commands. If so, then acts on the commands. If not,
    returns back what it needs for clarification.
    '''
    user_manager.load_user(user_id, channel=channel)

    # Set defaults.
    response = 'Type *@hackcoinbot help* for a guide!'
    attachment = []

    command_tokens = [w.lower() for w in command.strip().split(' ')]
    command_type = get_command_type(command_tokens)

    if command_type == 'price':
        response, attachment = get_price(command_tokens)

    if command_type == 'buy':
        response = buy(user_manager, command_tokens, user_id, channel=channel)

    if command_type == 'sell':
        response = sell(user_manager, command_tokens, user_id, channel=channel)

    if command_type == 'balance':
        response = user_manager.check_balance(user_id, channel=channel)

    if command_type == 'portfolio':
        response, attachment = portfolio(user_manager, user_id, channel=channel)

    if command_type == 'leaderboard':
        response = user_manager.check_leaderboard(user_id, channel=channel)

    if command_type == 'help':
        response = print_help()

    if command_type == 'meme':
        response = random.choice([
            ' litecoin is a shit investment ',
            ' :seansmile: buy ethereum now !!',
            ' is tonight the night we go to MARU ?? ',
            ' :blondesassyparrot: cash me ousside :blondesassyparrot: how bout dah :blondesassyparrot: ',
            ' you have been blessed by a r a r e p u p :doge: ',
            ' g o o d b o i ',
            ' :sakibwouldlikethat: sakib would like that '
        ])

    if command_type == 'greet':
        response = random.choice([
            ' :wave: ',
            ' :seansmile: ',
            ' :fastparrot: '
        ])

    print(datetime.now(), user_manager.users[user_id]['first_name'], command_type, command)

    if response is not None:
        slack_client.api_call('chat.postMessage', channel=channel,
                              text=response,
                              attachments=attachment,
                              as_user=True)

def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose.
    this parsing function returns None unless a message is
    directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output

    if not output_list:
        return None, None, None

    for output in output_list:
        command_text = None

        # Public channel
        if output and 'text' in output and AT_BOT in output['text']:
            command_text = output['text'].split(AT_BOT)[1].strip().lower()

        elif output and 'text' in output and 'channel' in output and \
            'user' in output and \
            not output.get('bot_id') and \
            output['user'] != BOT_ID and \
            is_private_message(slack_client, output['channel']):

            command_text = output['text'].strip().lower()

        if command_text is not None:
            # Return: the user, command, and channel
            return command_text, output['channel'], output['user']

    return None, None, None

def listen():
    # 0.25 second delay between reading from firehose
    READ_WEBSOCKET_DELAY = 0.25
    CHECK_MARKET_REMINDER = True

    if slack_client.rtm_connect():
        print('hackcoinbot says hello!')

        while True:
            if CHECK_MARKET_REMINDER and is_one_hour_left():
                slack_client.api_call('chat.postMessage',
                                      channel='#tradingfloor',
                                      text='<!channel> The stock market closes in *1 hour* :hourglass:',
                                      as_user=True)
                CHECK_MARKET_REMINDER = False

            command, channel, user_id = parse_slack_output(slack_client.rtm_read())
            if command and channel and user_id:
                handle_command(command, channel, user_id)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')


if __name__ == '__main__':
    listen()
