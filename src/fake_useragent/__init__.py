"""fake_useragent package public API.

Provides a small convenience layer exposing the public types and
constants: FakeUserAgent, UserAgent (alias), FakeUserAgentError,
UserAgentError, and VERSION.
"""

from fake_useragent.errors import FakeUserAgentError, UserAgentError
from fake_useragent.fake import FakeUserAgent, UserAgent
from fake_useragent.settings import __version__ as VERSION
