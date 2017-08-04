from datetime import datetime


def portfolio(user_manager, user_id, channel=None):
    response = user_manager.check_portfolio(user_id, channel=channel)
    now = datetime.now().strftime('%s')

    attachment = [
       {
           'fallback': 'Check Portfolio',
           'color': 'good',
           'author_name': user_manager.users[user_id]['first_name'],
           'author_icon': user_manager.get_user_thumbnail_url(user_id),
           'title': 'Portfolio',
           'text': response,
           'ts': now
       }
    ]
    return '', attachment
