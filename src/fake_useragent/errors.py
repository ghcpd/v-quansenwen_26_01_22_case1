"""Custom exceptions for the fake-useragent library."""

class FakeUserAgentError(Exception):
    """Base exception for fake-useragent errors."""
    pass


# common alias
UserAgentError = FakeUserAgentError
