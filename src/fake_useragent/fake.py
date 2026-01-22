"""Main module for generating fake user agent strings.

This module provides the FakeUserAgent class for generating random or
browser-specific user agent strings with filtering capabilities based on
browser type, operating system, platform, and version constraints.
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
    """Generate realistic fake user agent strings with filtering options.
    
    This class allows you to generate random or browser-specific user agent strings
    from a bundled database of real user agents. You can filter by browser type,
    operating system, platform, and version constraints.
    
    Args:
        browsers (Optional[Iterable[str]]): A list of browser names to filter by.
            Accepted values: 'chrome', 'firefox', 'safari', 'edge'.
            Defaults to all browsers.
        os (Optional[Iterable[str]]): A list of operating systems to filter by.
            Accepted values: 'win10', 'win7', 'macos', 'linux'.
            'windows' is automatically expanded to ['win10', 'win7'].
            Defaults to all OSes.
        min_version (float): Minimum browser version (inclusive). Defaults to 0.0.
        min_percentage (float): Minimum sampling percentage threshold. Defaults to 0.0.
        platforms (Optional[Iterable[str]]): A list of device types to filter by.
            Accepted values: 'pc', 'mobile', 'tablet'.
            Defaults to all platforms.
        fallback (str): A default user agent string to return if filtering fails
            or an error occurs. Defaults to a Chrome/Edge user agent on Windows.
        safe_attrs (Optional[Iterable[str]]): A list of attribute names that should
            not trigger user agent lookups (used internally for introspection).
            Defaults to an empty set.
    
    Raises:
        TypeError: If any parameter has an invalid type.
        ValueError: If a parameter value cannot be converted (e.g., non-numeric min_version).
    
    Attributes:
        browsers (list[str]): The filtered list of browser names.
        os (list[str]): The filtered list of operating system names.
        platforms (list[str]): The filtered list of device types.
        min_version (float): Minimum browser version filter.
        min_percentage (float): Minimum sampling percentage filter.
        fallback (str): Fallback user agent string.
        safe_attrs (set[str]): Set of safe attribute names.
        data_browsers (list[BrowserUserAgentData]): Loaded browser user agent data.
    
    Example:
        >>> ua = FakeUserAgent()
        >>> ua.random  # Get a random user agent string
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
        >>> ua.chrome  # Get a Chrome user agent string
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...'
        >>> ua.getRandom  # Get full user agent data object
        {'useragent': '...', 'browser': 'chrome', 'version': 122.0, ...}
        
        >>> ua_filtered = FakeUserAgent(browsers=['chrome', 'firefox'], os='linux')
        >>> ua_filtered.random  # Random Chrome or Firefox on Linux
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
        """Initialize a FakeUserAgent instance with filtering options.
        
        Args:
            browsers (Optional[Iterable[str]]): Browser names to include.
                Defaults to ['chrome', 'firefox', 'safari', 'edge'].
            os (Optional[Iterable[str]]): Operating systems to include.
                Defaults to ['win10', 'macos', 'linux'].
            min_version (float): Minimum browser version. Defaults to 0.0.
            min_percentage (float): Minimum sampling percentage. Defaults to 0.0.
            platforms (Optional[Iterable[str]]): Device types to include.
                Defaults to ['pc', 'mobile', 'tablet'].
            fallback (str): Fallback user agent if filtering fails.
            safe_attrs (Optional[Iterable[str]]): Attributes to exempt from user agent lookup.
        
        Raises:
            TypeError: If parameter types are invalid.
            ValueError: If numeric parameters cannot be converted.
        """
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

    # This method will return a filtered list of user agents.
    # The request parameter can be used to specify a browser.
    def _filter_useragents(
        self, request: Union[str, None] = None
    ) -> list[BrowserUserAgentData]:
        """Filter user agents based on configured constraints and optional browser request.
        
        This method filters the loaded user agent database by the instance's configuration
        (browsers, OS, platforms, versions, and percentage thresholds). If a specific
        browser is requested, further filters by that browser name.
        
        Args:
            request (Union[str, None]): Optional specific browser name to filter by
                (e.g., 'chrome', 'firefox'). If None, returns all matching user agents
                for the configured browsers.
        
        Returns:
            list[BrowserUserAgentData]: A list of user agent dictionaries matching
                all configured filters and the optional browser request.
        
        Note:
            - Returns an empty list if no user agents match all filters.
            - The returned list may be empty even for valid browsers if no user agents
              match the version or percentage constraints.
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

    # This method will return an object
    # Usage: ua.getBrowser('firefox')
    def getBrowser(self, request: str) -> BrowserUserAgentData:
        """Get a random user agent dictionary for a specific browser.
        
        This method returns a complete user agent data object (dictionary) for a randomly
        selected user agent of the requested browser type, applying all configured filters.
        
        Args:
            request (str): The browser name to get a user agent for. Case-insensitive.
                Accepted values include: 'chrome', 'firefox', 'safari', 'edge', and aliases
                defined in settings.SHORTCUTS (e.g., 'google' -> 'chrome', 'ff' -> 'firefox').
                Special value 'random' returns a random browser from the configured browsers.
        
        Returns:
            BrowserUserAgentData: A user agent data dictionary containing:
                - useragent (str): The user agent string
                - browser (str): The browser name
                - version (float): The browser version
                - os (str): The operating system
                - type (str): The device type (pc/mobile/tablet)
                - system (str): System description
                - percent (float): Sampling percentage
        
        Note:
            - If filtering fails or results are empty, returns a fallback user agent
              object with hardcoded values.
            - Unrecognized browser names that don't match any user agent data
              will trigger the fallback.
            - The returned dictionary structure is guaranteed by BrowserUserAgentData.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> firefox_data = ua.getBrowser('firefox')
            >>> print(firefox_data['useragent'])  # Full user agent string
            >>> print(firefox_data['version'])    # Version number
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

    # This method will use the method below, returning a string
    # Usage: ua['random']
    def __getitem__(self, attr: str) -> Union[str, Any]:
        """Get a user agent string using dictionary-style access.
        
        This method enables dictionary-style access to user agent strings,
        delegating to __getattr__ for the actual lookup.
        
        Args:
            attr (str): The browser name or special attribute name to retrieve.
                Supports the same values as __getattr__.
        
        Returns:
            Union[str, Any]: The user agent string, or fallback if lookup fails.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua['chrome'])    # Same as ua.chrome
            >>> print(ua['random'])    # Same as ua.random
        
        Note:
            - Equivalent to calling __getattr__(attr).
            - Returns user agent strings (not full data objects).
        """
        return self.__getattr__(attr)

    # This method will returns a string
    # Usage: ua.random
    def __getattr__(self, attr: str) -> Union[str, Any]:
        """Get a user agent string using attribute access (dot notation).
        
        This method handles dynamic attribute access to return user agent strings.
        It applies the same filtering as getBrowser but returns only the user agent
        string (not the full data object).
        
        Args:
            attr (str): The browser name or attribute to retrieve. Case-insensitive.
                Supported values:
                - 'random': A random user agent from all configured browsers
                - 'chrome', 'firefox', 'safari', 'edge': Browser-specific user agents
                - Aliases defined in settings.SHORTCUTS (e.g., 'google', 'ff')
                - Attributes in safe_attrs are excluded from user agent lookup
        
        Returns:
            Union[str, Any]: The user agent string for the requested browser,
                or the fallback string if lookup fails.
        
        Raises:
            (implicitly) No exceptions are raised - errors are caught and suppressed
                with a fallback being returned.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua.random)      # Random user agent string
            >>> print(ua.chrome)      # Chrome-specific user agent
            >>> print(ua.firefox)     # Firefox-specific user agent
            >>> ua.getFirefox  # Note: different from ua.firefox (returns data object)
        
        Note:
            - If the attribute is in safe_attrs, delegates to parent __getattribute__.
            - Unrecognized browser names return the fallback string.
            - All exceptions during lookup are silently suppressed.
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
            str: A Chrome user agent string matching configured filters, or fallback.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua.chrome)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
        """
        return self.__getattr__("chrome")

    @property
    def googlechrome(self) -> str:
        """Get a random Chrome user agent string (alias for chrome).
        
        Returns:
            str: A Chrome user agent string matching configured filters, or fallback.
        
        Note:
            This property is an alias for the chrome property.
        """
        return self.chrome

    @property
    def edge(self) -> str:
        """Get a random Edge user agent string.
        
        Returns:
            str: An Edge user agent string matching configured filters, or fallback.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua.edge)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
        """
        return self.__getattr__("edge")

    @property
    def firefox(self) -> str:
        """Get a random Firefox user agent string.
        
        Returns:
            str: A Firefox user agent string matching configured filters, or fallback.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua.firefox)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:...) Gecko/...'
        """
        return self.__getattr__("firefox")

    @property
    def ff(self) -> str:
        """Get a random Firefox user agent string (alias for firefox).
        
        Returns:
            str: A Firefox user agent string matching configured filters, or fallback.
        
        Note:
            This property is an alias for the firefox property.
        """
        return self.firefox

    @property
    def safari(self) -> str:
        """Get a random Safari user agent string.
        
        Returns:
            str: A Safari user agent string matching configured filters, or fallback.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua.safari)
            'Mozilla/5.0 (Macintosh; Intel Mac OS X ...) AppleWebKit/537.36...'
        """
        return self.__getattr__("safari")

    @property
    def random(self) -> str:
        """Get a random user agent string from all configured browsers.
        
        Returns:
            str: A random user agent string matching configured filters.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> print(ua.random)
            # Randomly returns Chrome, Firefox, Safari, or Edge
        """
        return self.__getattr__("random")

    # The following 'get' methods return an object rather than only the UA string
    @property
    def getFirefox(self) -> BrowserUserAgentData:
        """Get a random Firefox user agent data object.
        
        Returns:
            BrowserUserAgentData: A complete Firefox user agent data dictionary
                with useragent string and metadata.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> firefox_data = ua.getFirefox
            >>> print(firefox_data['useragent'])
            >>> print(firefox_data['version'])
        
        Note:
            Unlike firefox property which returns a string, this returns
            the full user agent data object.
        """
        return self.getBrowser("firefox")

    @property
    def getChrome(self) -> BrowserUserAgentData:
        """Get a random Chrome user agent data object.
        
        Returns:
            BrowserUserAgentData: A complete Chrome user agent data dictionary
                with useragent string and metadata.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> chrome_data = ua.getChrome
            >>> print(chrome_data['useragent'])
            >>> print(chrome_data['version'])
        
        Note:
            Unlike chrome property which returns a string, this returns
            the full user agent data object.
        """
        return self.getBrowser("chrome")

    @property
    def getEdge(self) -> BrowserUserAgentData:
        """Get a random Edge user agent data object.
        
        Returns:
            BrowserUserAgentData: A complete Edge user agent data dictionary
                with useragent string and metadata.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> edge_data = ua.getEdge
            >>> print(edge_data['useragent'])
            >>> print(edge_data['version'])
        
        Note:
            Unlike edge property which returns a string, this returns
            the full user agent data object.
        """
        return self.getBrowser("edge")

    @property
    def getSafari(self) -> BrowserUserAgentData:
        """Get a random Safari user agent data object.
        
        Returns:
            BrowserUserAgentData: A complete Safari user agent data dictionary
                with useragent string and metadata.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> safari_data = ua.getSafari
            >>> print(safari_data['useragent'])
            >>> print(safari_data['version'])
        
        Note:
            Unlike safari property which returns a string, this returns
            the full user agent data object.
        """
        return self.getBrowser("safari")

    @property
    def getRandom(self) -> BrowserUserAgentData:
        """Get a random user agent data object from all configured browsers.
        
        Returns:
            BrowserUserAgentData: A complete user agent data dictionary
                with useragent string and metadata.
        
        Example:
            >>> ua = FakeUserAgent()
            >>> random_data = ua.getRandom
            >>> print(random_data['useragent'])
            >>> print(random_data['browser'])
            >>> print(random_data['version'])
        
        Note:
            Unlike random property which returns a string, this returns
            the full user agent data object.
        """
        return self.getBrowser("random")


# common alias
UserAgent = FakeUserAgent
