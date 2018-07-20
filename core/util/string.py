def clear_string(string):

    if not string:
        return string

    return string \
        .replace('.', '') \
        .replace('-', '') \
        .replace('/', '') \
        .replace('(', '') \
        .replace(')', '') \
        .replace('+', '') \
        .replace(' ', '')


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
