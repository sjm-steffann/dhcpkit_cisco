import codecs

from dhcpkit.utils import normalise_hex

acceptable_characters = [chr(c) for c in range(32, 127)]


def hex_as_ascii(value):
    try:
        decoded = codecs.decode(value.encode('ascii'), 'hex').decode('ascii')
        if all(c in acceptable_characters for c in decoded):
            return True, decoded
    except UnicodeDecodeError:
        pass

    return False, normalise_hex(value, include_colons=True)


def display_hex(value):
    as_ascii, display_value = hex_as_ascii(value)

    if as_ascii:
        return '"' + display_value + '"'
    else:
        return display_value
