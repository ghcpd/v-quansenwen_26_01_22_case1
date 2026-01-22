"""Fake User Agent library for generating random browser user agent strings.

This library provides a simple API to generate realistic user agent strings for
various browsers, operating systems, and platforms. It is useful for web scraping,
testing, and any application that needs to simulate different browser environments.

Examples:
    Basic usage::

        from fake_useragent import FakeUserAgent
        ua = FakeUserAgent()
        print(ua.chrome)  # Get a Chrome user agent
        print(ua.random)  # Get a random user agent
"""

from fake_useragent.errors import FakeUserAgentError, UserAgentError
from fake_useragent.fake import FakeUserAgent, UserAgent
from fake_useragent.settings import __version__ as VERSION
