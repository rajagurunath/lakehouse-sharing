import uuid


def get_random_uuid():
    return str(uuid.uuid4())


def get_random_uuid_hex():
    return str(uuid.uuid4().hex)
