
def clear_string(string):
    if not string:
        return ''

    return str(string) \
        .replace('.', '') \
        .replace('-', '') \
        .replace('/', '') \
        .replace('(', '') \
        .replace(')', '') \
        .replace(' ', '')
