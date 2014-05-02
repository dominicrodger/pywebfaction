import string


def email_to_mailbox_name(email_address):
    if not email_address:
        raise ValueError("E-mail addresses cannot be empty.")

    email_address = email_address.lower()
    valid_characters = string.ascii_letters + string.digits + '_'

    def is_valid_character(c):
        return c in valid_characters

    def make_valid(c):
        if is_valid_character(c):
            return c

        if c == '@':
            return '_'

        return ''

    joined_up = ''.join([make_valid(c) for c in email_address])

    if joined_up == '_' * len(joined_up):
        raise ValueError(
            "Mailbox names must contain at least one valid "
            "character."
        )

    return joined_up
