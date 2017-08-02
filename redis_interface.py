from functools import wraps

import redis

from utils import diff


class Delete:
    pass


client = redis.StrictRedis(host='localhost', port=6379, db=0)

def prefix(pre):
    def inner(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            id = args[0]
            return func(
                '{}:{}'.format(pre, id),
                *args[1:],
                **kwargs
            )
        return wrapped
    return inner

def _get(key, fields=[], attr=None):
    if attr == 'vals':
        return client.hvals(key)
    elif attr == 'keys':
        return client.hkeys(key)
    elif attr == 'len':
        return client.hlen(key)

    if fields:
        return client.hmget(key, fields)
    else:
        return client.hgetall(key)

@prefix('user')
def get_user(id, fields=[], attr=None):
    return _get(id, fields=fields, attr=attr)

@prefix('portfolio')
def get_portfolio(id, fields=[], attr=None):
    return _get(id, fields=fields, attr=attr)

def _set(key, val):
    to_delete = []
    to_set = []
    for k, v in val.items():
        if isinstance(v, Delete):
            to_delete.append(k)
        else:
            to_set.append(k)

    client.hmset(key, {
        k: val[k] for k in to_set
    })
    client.hdel(key, to_delete)

@prefix('user')
def set_user(id, val):
    _set(id, val)

@prefix('portfolio')
def set_portfolio(id, val):
    _set(id, val)

def _delete(key):
    client.delete(key)

@prefix('user')
def delete_user(id):
    _delete(id)

@prefix('portfolio')
def delete_portfolio(id):
    _delete(id)

def dump():
    user_keys = client.keys('user:*')
    portfolio_keys = client.keys('portfolio:*')

    users = {
        k.split(':')[1]: client.hgetall(k) for k in user_keys
    }
    for key in portfolio_keys:
        id = key.split(':')[1]

        users['portfolio'] = client.hgetall(key)

    return users

def load():
    pass
