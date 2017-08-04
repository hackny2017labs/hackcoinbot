from decimal import Decimal, InvalidOperation


def coerce_decimal(s):
    val = None

    try:
        val = Decimal(s)
    except InvalidOperation:
        pass

    return val

