class SessionError(Exception):
    """An expected session failure whose message tells the operator what went wrong.

    Logged without a traceback: the message is the useful part. Any other
    exception is treated as a bug and logged with its traceback.
    """
