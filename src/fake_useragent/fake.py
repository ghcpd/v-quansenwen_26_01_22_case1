"""Main module containing the FakeUserAgent class and related functionality.

This module implements the core FakeUserAgent class, which provides methods and
properties for generating user agent strings for different browsers and platforms.
It also includes utility functions for parameter validation and filtering.
"""

import random
from collections.abc import Iterable
from typing import Any, Optional, Union

from fake_useragent import settings
from fake_useragent.log import logger
from fake_useragent.utils import BrowserUserAgentData, load


def _ensure_iterable(
    *, default: Iterable[str], **kwarg: Optional[Iterable[str]]
) -> list[str]:
    """Ensure the given value is an Iterable and convert it to a list.

    Args:
        default (Iterable[str]): Default iterable to use if value is `None`.
        **kwarg (Optional[Iterable[str]]): A single keyword argument containing the value to check
            and convert.

    Raises:
        ValueError: If more than one keyword argument is provided.
        TypeError: If the value is not None, not a str, and not iterable.

    Returns:
        list[str]: A list containing the items from the iterable.
    """
    if len(kwarg) != 1:
        raise ValueError(
            f"ensure_iterable expects exactly one keyword argument but got {len(kwarg)}."
        )

    param_name, value = next(iter(kwarg.items()))

    if value is None:
        return list(default)
    if isinstance(value, str):
        return [value]

    try:
        return list(value)
    except TypeError as te:
        raise TypeError(
            f"'{param_name}' must be an iterable of str, a single str, or None but got "
            f"{type(value).__name__}."
        ) from te


def _ensure_float(value: Any) -> float:
    """Ensure the given value is a float.

    Args:
        value (Any): The value to check and convert.

    Raises:
        ValueError: If the value is not a float.

    Returns:
        float: The float value.
    """
    try:
        return float(value)
    except ValueError as ve:
        msg = f"Value must be convertible to float but got {value}."
        raise ValueError(msg) from ve


class FakeUserAgent:
    """Generate random user agent strings for various browsers and platforms.

    This class provides multiple ways to access user agent strings:
    - Property access (e.g., ua.chrome, ua.firefox, ua.random)
    - Dictionary-style access (e.g., ua['chrome'])
    - Method access via getBrowser() and related methods

    User agents can be filtered by browser type, operating system, platform,
    version, and usage percentage.

    Args:
        browsers (Optional[Iterable[str]]): List of browser names to include.
            Defaults to ["chrome", "firefox", "safari", "edge"].
        os (Optional[Iterable[str]]): List of operating systems to include.
            Defaults to ["win10", "macos", "linux"].
            Special handling: "windows" expands to ["win10", "win7"].
        min_version (float): Minimum browser version to include. Defaults to 0.0.
        min_percentage (float): Minimum usage percentage to include. Defaults to 0.0.
        platforms (Optional[Iterable[str]]): List of platform types to include.
            Defaults to ["pc", "mobile", "tablet"].
        fallback (str): User agent string to return if no matching user agents are found.
            Defaults to a Chrome 122 on Windows 10 user agent string.
        safe_attrs (Optional[Iterable[str]]): Attribute names that should bypass
            the custom __getattr__ handler and use standard attribute access.
            Defaults to empty set.

    Raises:
        TypeError: If parameters are not of the expected types.
        ValueError: If parameter values cannot be converted to expected types.

    Examples:
        Basic usage::

            ua = FakeUserAgent()
            print(ua.chrome)        # Random Chrome user agent
            print(ua.firefox)       # Random Firefox user agent
            print(ua.random)        # Random user agent from any browser
            print(ua['safari'])     # Dictionary-style access

        Filtered usage::

            ua = FakeUserAgent(browsers=['chrome'], os=['macos'])
            print(ua.chrome)        # Chrome user agent for macOS only

        Get full browser data::

            ua = FakeUserAgent()
            data = ua.getChrome     # Returns BrowserUserAgentData dict
            print(data['useragent'])
            print(data['version'])
    """

    def __init__(  # noqa: PLR0913
        self,
        browsers: Optional[Iterable[str]] = None,
        os: Optional[Iterable[str]] = None,
        min_version: float = 0.0,
        min_percentage: float = 0.0,
        platforms: Optional[Iterable[str]] = None,
        fallback: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
        ),
        safe_attrs: Optional[Iterable[str]] = None,
    ):
        self.browsers = _ensure_iterable(
            browsers=browsers, default=["chrome", "firefox", "safari", "edge"]
        )

        os = _ensure_iterable(os=os, default=["win10", "macos", "linux"])
        self.os = [
            item
            for os_name in os
            for item in settings.OS_REPLACEMENTS.get(os_name, [os_name])
        ]

        self.min_percentage = _ensure_float(min_percentage)
        self.min_version = _ensure_float(min_version)

        self.platforms = _ensure_iterable(
            platforms=platforms, default=["pc", "mobile", "tablet"]
        )

        if not isinstance(fallback, str):
            msg = f"fallback must be a str but got {type(fallback).__name__}."
            raise TypeError(msg)
        self.fallback = fallback

        safe_attrs = _ensure_iterable(safe_attrs=safe_attrs, default=set())
        str_safe_attrs = [isinstance(attr, str) for attr in safe_attrs]
        if not all(str_safe_attrs):
            bad_indices = [
                idx for idx, is_str in enumerate(str_safe_attrs) if not is_str
            ]
            msg = f"safe_attrs must be an iterable of str but indices {bad_indices} are not."
            raise TypeError(msg)
        self.safe_attrs = set(safe_attrs)

        # Next, load our local data file into memory (browsers.json)
        self.data_browsers = load()

    def _filter_useragents(
        self, request: Union[str, None] = None
    ) -> list[BrowserUserAgentData]:
        """Filter user agents based on instance configuration and optional browser request.

        Applies filters based on the instance's browsers, os, platforms, min_version,
        and min_percentage settings. If a specific browser is requested, only user
        agents matching that browser will be returned.

        Args:
            request (Union[str, None]): Optional browser name to filter by.
                If None, returns all user agents matching instance filters.
                If specified, further filters to only the requested browser.

        Returns:
            list[BrowserUserAgentData]: List of user agent data dictionaries that
                match all applicable filters. May be empty if no matches are found.
        """
        # filter based on browser, os, platform and version.
        filtered_useragents = list(
            filter(
                lambda x: x["browser"] in self.browsers
                and x["os"] in self.os
                and x["type"] in self.platforms
                and x["version"] >= self.min_version
                and x["percent"] >= self.min_percentage,
                self.data_browsers,
            )
        )
        # filter based on a specific browser request
        if request:
            filtered_useragents = list(
                filter(lambda x: x["browser"] == request, filtered_useragents)
            )

        return filtered_useragents

    def getBrowser(self, request: str) -> BrowserUserAgentData:
        """Get a random user agent data dictionary for the specified browser.

        This method normalizes the request string by applying replacements and
        shortcuts, then returns a randomly selected user agent that matches
        the request and instance filters.

        The request string is normalized by:
        1. Removing spaces and underscores
        2. Converting to lowercase
        3. Applying shortcut mappings (e.g., 'ff' -> 'firefox')

        Args:
            request (str): Browser name to get user agent for. Special value
                'random' returns a user agent from any configured browser.
                Common values: 'chrome', 'firefox', 'safari', 'edge', 'random'.

        Returns:
            BrowserUserAgentData: Dictionary containing user agent information
                including 'useragent' (str), 'browser' (str), 'os' (str),
                'version' (float), 'percent' (float), 'type' (str), and
                'system' (str). If no matching user agents are found, returns
                a fallback dictionary with the configured fallback user agent.

        Examples:
            Get a Firefox user agent::

                data = ua.getBrowser('firefox')
                print(data['useragent'])
        """
        try:
            # Handle request value
            for value, replacement in settings.REPLACEMENTS.items():
                request = request.replace(value, replacement)
            request = request.lower()
            request = settings.SHORTCUTS.get(request, request)

            if request == "random":
                # Filter the browser list based on the browsers array using lambda
                # And based on OS list
                # And percentage is bigger then min percentage
                # And convert the iterator back to a list
                filtered_browsers = self._filter_useragents()
            else:
                # Or when random isn't select, we filter the browsers array based on the 'request' using lamba
                # And based on OS list
                # And percentage is bigger then min percentage
                # And convert the iterator back to a list
                filtered_browsers = self._filter_useragents(request=request)

            # Pick a random browser user-agent from the filtered browsers
            # And return the full dict
            return random.choice(filtered_browsers)  # noqa: S311
        except (KeyError, IndexError):
            logger.warning(
                f"Error occurred during getting browser: {request}, "
                "but was suppressed with fallback.",
            )
            # Return fallback object
            return {
                "useragent": self.fallback,
                "percent": 100.0,
                "type": "pc",
                "system": "Chrome 122.0 Win10",
                "browser": "chrome",
                "version": 122.0,
                "os": "win10",
            }

    def __getitem__(self, attr: str) -> Union[str, Any]:
        """Get a user agent string using dictionary-style access.

        This method delegates to __getattr__ to provide dictionary-style
        access to user agent strings.

        Args:
            attr (str): Browser name to get user agent string for.
                Examples: 'chrome', 'firefox', 'safari', 'edge', 'random'.

        Returns:
            Union[str, Any]: User agent string for the requested browser,
                or the fallback string if no match is found.

        Examples:
            Access user agents with bracket notation::

                ua = FakeUserAgent()
                print(ua['chrome'])
                print(ua['random'])
        """
        return self.__getattr__(attr)

    def __getattr__(self, attr: str) -> Union[str, Any]:
        """Get a user agent string using attribute-style access.

        This method normalizes the attribute name and returns a randomly
        selected user agent string matching the request and instance filters.
        If the attribute is in safe_attrs, standard attribute access is used.

        The attribute name is normalized by:
        1. Removing spaces and underscores
        2. Converting to lowercase
        3. Applying shortcut mappings (e.g., 'ff' -> 'firefox')

        Args:
            attr (str): Browser name to get user agent string for.
                Special value 'random' returns a user agent from any browser.
                Common values: 'chrome', 'firefox', 'safari', 'edge', 'random'.

        Returns:
            Union[str, Any]: User agent string for the requested browser.
                Returns the configured fallback string if no matching user
                agents are found. For safe_attrs, returns the actual attribute value.

        Examples:
            Access user agents as attributes::

                ua = FakeUserAgent()
                print(ua.chrome)
                print(ua.firefox)
                print(ua.random)
        """
        if attr in self.safe_attrs:
            return super(UserAgent, self).__getattribute__(attr)

        try:
            # Handle input value
            for value, replacement in settings.REPLACEMENTS.items():
                attr = attr.replace(value, replacement)
            attr = attr.lower()
            attr = settings.SHORTCUTS.get(attr, attr)

            if attr == "random":
                # Filter the browser list based on the browsers array using lambda
                # And based on OS list
                # And percentage is bigger then min percentage
                # And convert the iterator back to a list
                filtered_browsers = self._filter_useragents()
            else:
                # Or when random isn't select, we filter the browsers array based on the 'attr' using lamba
                # And based on OS list
                # And percentage is bigger then min percentage
                # And convert the iterator back to a list
                filtered_browsers = self._filter_useragents(request=attr)

            # Pick a random browser user-agent from the filtered browsers
            # And return the useragent string.
            return random.choice(filtered_browsers).get("useragent")  # noqa: S311
        except (KeyError, IndexError):
            logger.warning(
                f"Error occurred during getting browser: {attr}, "
                "but was suppressed with fallback.",
            )
            return self.fallback

    @property
    def chrome(self) -> str:
        """Get a random Chrome user agent string.

        Returns:
            str: A user agent string for Chrome browser, or the fallback
                string if no Chrome user agents match the instance filters.
        """
        return self.__getattr__("chrome")

    @property
    def googlechrome(self) -> str:
        """Get a random Google Chrome user agent string.

        Alias for the chrome property.

        Returns:
            str: A user agent string for Chrome browser, or the fallback
                string if no Chrome user agents match the instance filters.
        """
        return self.chrome

    @property
    def edge(self) -> str:
        """Get a random Microsoft Edge user agent string.

        Returns:
            str: A user agent string for Edge browser, or the fallback
                string if no Edge user agents match the instance filters.
        """
        return self.__getattr__("edge")

    @property
    def firefox(self) -> str:
        """Get a random Firefox user agent string.

        Returns:
            str: A user agent string for Firefox browser, or the fallback
                string if no Firefox user agents match the instance filters.
        """
        return self.__getattr__("firefox")

    @property
    def ff(self) -> str:
        """Get a random Firefox user agent string.

        Alias for the firefox property.

        Returns:
            str: A user agent string for Firefox browser, or the fallback
                string if no Firefox user agents match the instance filters.
        """
        return self.firefox

    @property
    def safari(self) -> str:
        """Get a random Safari user agent string.

        Returns:
            str: A user agent string for Safari browser, or the fallback
                string if no Safari user agents match the instance filters.
        """
        return self.__getattr__("safari")

    @property
    def random(self) -> str:
        """Get a random user agent string from any configured browser.

        Returns:
            str: A user agent string randomly selected from all browsers
                that match the instance filters, or the fallback string if
                no user agents match the filters.
        """
        return self.__getattr__("random")

    # The following 'get' methods return an object rather than only the UA string
    @property
    def getFirefox(self) -> BrowserUserAgentData:
        """Get complete Firefox user agent data including metadata.

        Returns:
            BrowserUserAgentData: Dictionary containing Firefox user agent
                information including 'useragent', 'browser', 'os', 'version',
                'percent', 'type', and 'system'. Returns fallback data if no
                Firefox user agents match the instance filters.
        """
        return self.getBrowser("firefox")

    @property
    def getChrome(self) -> BrowserUserAgentData:
        """Get complete Chrome user agent data including metadata.

        Returns:
            BrowserUserAgentData: Dictionary containing Chrome user agent
                information including 'useragent', 'browser', 'os', 'version',
                'percent', 'type', and 'system'. Returns fallback data if no
                Chrome user agents match the instance filters.
        """
        return self.getBrowser("chrome")

    @property
    def getEdge(self) -> BrowserUserAgentData:
        """Get complete Microsoft Edge user agent data including metadata.

        Returns:
            BrowserUserAgentData: Dictionary containing Edge user agent
                information including 'useragent', 'browser', 'os', 'version',
                'percent', 'type', and 'system'. Returns fallback data if no
                Edge user agents match the instance filters.
        """
        return self.getBrowser("edge")

    @property
    def getSafari(self) -> BrowserUserAgentData:
        """Get complete Safari user agent data including metadata.

        Returns:
            BrowserUserAgentData: Dictionary containing Safari user agent
                information including 'useragent', 'browser', 'os', 'version',
                'percent', 'type', and 'system'. Returns fallback data if no
                Safari user agents match the instance filters.
        """
        return self.getBrowser("safari")

    @property
    def getRandom(self) -> BrowserUserAgentData:
        """Get complete user agent data for a random browser including metadata.

        Returns:
            BrowserUserAgentData: Dictionary containing user agent information
                for a randomly selected browser including 'useragent', 'browser',
                'os', 'version', 'percent', 'type', and 'system'. Returns fallback
                data if no user agents match the instance filters.
        """
        return self.getBrowser("random")


# common alias
UserAgent = FakeUserAgent
