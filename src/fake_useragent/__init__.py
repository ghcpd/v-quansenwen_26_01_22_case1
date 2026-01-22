"""A library for generating fake user agent strings.

This module provides the FakeUserAgent class, which allows you to generate
random or browser-specific user agent strings. It's useful for web scraping,
testing, and other scenarios where you need realistic user agent data.

Example:
    >>> from fake_useragent import FakeUserAgent
    >>> ua = FakeUserAgent()
    >>> print(ua.random)  # Random user agent string
    >>> print(ua.chrome)  # Chrome user agent string
    >>> ua_data = ua.getRandom  # Get full user agent data object
"""

from fake_useragent.errors import FakeUserAgentError, UserAgentError
from fake_useragent.fake import FakeUserAgent, UserAgent
from fake_useragent.settings import __version__ as VERSION
