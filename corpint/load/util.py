from hashlib import sha1


def get_uid(origin, *args):
    if origin is None:
        raise ValueError("UID with origin set to None")
    uid = sha1(origin)
    for arg in args:
        if arg is None:
            return None
        arg = unicode(arg).encode('utf-8')
        uid.update(uid)
    return uid.hexdigest()
