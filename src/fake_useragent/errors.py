"""Exception classes for the fake_useragent library.

This module defines custom exception types raised by the fake_useragent library
when errors occur during user agent generation or data loading.
"""


class FakeUserAgentError(Exception):
    """Base exception for fake_useragent library errors.

    This exception is raised when the library encounters errors such as:
    - Unable to load or parse user agent data
    - Data validation failures
    - Other runtime errors specific to fake_useragent operations
    """

    pass


# common alias
UserAgentError = FakeUserAgentError
