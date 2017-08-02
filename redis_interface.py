from decimal import Decimal
from functools import wraps
import os

import redis

from utils import diff


class Delete:
    pass

host = 'localhost'
if os.environ.get('is_docker'):
    host = 'redis'
client = redis.StrictRedis(host=host, port=6379, db=0)

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
    user = _get(id, fields=fields, attr=attr)
    user['coins'] = Decimal(user.get('coins') or '0')

    return user

@prefix('positions')
def get_positions(id, fields=[], attr=None):
    positions = _get(id, fields=fields, attr=attr)

    for k, v in positions.items():
        vals = [Decimal(x) for x in v.split(':')]
        positions[k.upper()] = {
            'shares': vals[0],
            'average_price': vals[1]
        }

    return positions

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
    val['coins'] = val['coins']
    _set(id, val)

@prefix('positions')
def set_positions(id, val):
    data = {
        k.upper(): '{}:{}'.format(
            str(v['shares']),
            str(v['average_price'])
        ) for k, v in val.items()
    }
    _set(id, data)

def _delete(key):
    client.delete(key)

@prefix('user')
def delete_user(id):
    _delete(id)

@prefix('positions')
def delete_positions(id):
    _delete(id)

def dump():
    user_keys = client.keys('user:*')
    portfolio_keys = client.keys('positions:*')

    users = {}
    for key in portfolio_keys:
        id = key.split(':')[1]
        users[id] = get_user(id)
        users[id]['positions'] = get_positions(id)

    return users

def load(data):
    for id, val in data.items():
        positions = val.get('positions')

        if positions:
            del val['positions']
            set_positions(id, positions)

        set_user(id, val)
