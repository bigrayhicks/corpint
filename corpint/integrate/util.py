from hashlib import sha1


def sorttuple(a, b):
    return (max(a, b), min(a, b))


def merkle(items):
    uid = sha1()
    for item in sorted(set(items)):
        uid.update(unicode(item).encode('utf-8'))
    return uid.hexdigest()
