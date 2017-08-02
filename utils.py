def diff(src, updated):
    """
    Diff function to diff lists/dicts. For dicts, it'll return
    lists of keys. For lists, it'll return actual values.
    """
    diff = {}

    src_keys = set(src)
    updated_keys = set(updated)

    diff['deleted'] = list(src_keys - updated_keys)
    diff['added'] = list(updated_keys - src_keys)
    diff['modified'] = [
        k for k in src_keys & updated_keys
    ]
