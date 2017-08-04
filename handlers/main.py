def get_command_type(command_tokens):
    if not command_tokens:
        return None

    if '$' in command_tokens[0]:
        return 'price'

    if command_tokens[0] in ('buy', 'b'):
        return 'buy'

    if command_tokens[0] in ('sell', 's'):
        return 'sell'

    if command_tokens[0] == 'balance':
        return 'balance'

    if command_tokens[0] in ('portfolio', 'p'):
        return 'portfolio'

    if command_tokens[0] in ('leader', 'leaderboard', 'l', 'top'):
        return 'leaderboard'

    if command_tokens[0] == 'help':
        return 'help'

    if command_tokens[0] in ('hello', 'hey', 'greet', 'hi'):
        return 'greet'

    if command_tokens[0] in ('meme', 'shit', 'shitpost'):
        return 'meme'

def is_private_message(slack_client, channel_id):
    im_ids = [
        x['id']
        for x in
        slack_client.api_call('im.list')['ims']
    ]

    return channel_id in set(im_ids)
