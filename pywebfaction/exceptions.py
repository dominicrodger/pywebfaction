import ast


EXCEPTION_TYPE_PREFIX = "<class 'webfaction_api.exceptions."
EXCEPTION_TYPE_SUFFIX = "'>"


def _parse_exc_type(exc_type):
    # This is horribly hacky, but there's not a particularly elegant
    # way to go from the exception type to a string representing that
    # exception.
    if not exc_type.startswith(EXCEPTION_TYPE_PREFIX):
        return None

    if not exc_type.endswith(EXCEPTION_TYPE_SUFFIX):
        return None

    return exc_type[len(EXCEPTION_TYPE_PREFIX):len(EXCEPTION_TYPE_SUFFIX) * -1]


def _parse_exc_message(exc_message):
    if not exc_message:
        return None

    message = ast.literal_eval(exc_message)

    if isinstance(message, list):
        if not message:
            return None
        return message[0]

    return None


class WebFactionFault(Exception):
    def __init__(self, underlying):
        self.underlying_fault = underlying
        try:
            exc_type, exc_message = underlying.faultString.split(':', 1)
            self.exception_type = _parse_exc_type(exc_type)
            self.exception_message = _parse_exc_message(exc_message)
        except ValueError:
            self.exception_type = None
            self.exception_message = None
