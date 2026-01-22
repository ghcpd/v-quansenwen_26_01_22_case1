"""Exception classes for the fake_useragent module.

This module defines custom exception classes used by fake_useragent
to distinguish library-specific errors from other exceptions.
"""


class FakeUserAgentError(Exception):
    """Exception raised when an error occurs in the fake_useragent library.
    
    This exception is raised when user agent data cannot be loaded,
    filtered results are empty, or other internal errors occur.
    """
    pass


# common alias
UserAgentError = FakeUserAgentError

