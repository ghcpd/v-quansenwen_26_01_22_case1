"""Exceptions used by the fake_useragent package.

The module defines the public exception class raised for errors in
the package.
"""

class FakeUserAgentError(Exception):
    """Base exception for errors raised by fake_useragent.

    The exception may include optional additional context in its args
    but no structured attributes are guaranteed by the implementation.
    """
    pass


# common alias
UserAgentError = FakeUserAgentError
