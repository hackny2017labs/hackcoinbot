import os
import time
from slackclient import SlackClient
import random

from handlers import get_price, get_command_type, buy, sell
from users import HackcoinUser

# env variable bot_id
BOT_ID = os.environ.get("SLACK_BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel, user_id):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    user_object = HackcoinUser(
        user_id,
        channel = channel
    )

    response = random.choice([
        " litecoin is a shit investment ",
        " buy eth now !!",
        " maru?? ",
        " i don't talk so good right now",
        " pork buns ",
        " r a r e p u p "
    ])

    command_tokens = [w.lower() for w in command.strip().split(" ")]
    command_type = get_command_type(command_tokens)

    if command_type == "price":
        response = get_price(command_tokens)

    if command_type == "buy":
        response = buy(user_object, command_tokens)

    if command_type == "sell":
        response = sell(user_object, command_tokens)

    if response is not None:
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # Return: the user, command, and channel
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], \
                       output['user']
    return None, None, None

def listen():
    # 1 second delay between reading from firehose
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("hackcoinbot says hello!")

        while True:
            command, channel, user_id = parse_slack_output(slack_client.rtm_read())
            if command and channel and user_id:
                handle_command(command, channel, user_id)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


if __name__ == "__main__":
    listen()
