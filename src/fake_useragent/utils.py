"""Utility functions and data structures for the fake_useragent library.

This module provides the BrowserUserAgentData type definition and the load()
function for reading user agent data from the bundled JSON data file.
"""

import json
import sys
from typing import TypedDict, Union

# We need files() from Python 3.10 or higher
if sys.version_info >= (3, 10):
    import importlib.resources as ilr
else:
    import importlib_resources as ilr

from fake_useragent.errors import FakeUserAgentError
from fake_useragent.log import logger


class BrowserUserAgentData(TypedDict):
    """TypedDict representing browser user agent data and metadata.

    This dictionary structure contains all information about a user agent string,
    including the string itself and associated metadata such as browser type,
    version, operating system, and device type.
    """

    useragent: str
    """The user agent string."""
    percent: float
    """Sampling probability for this user agent when random sampling. Currently has no effect."""
    type: str
    """The device type for this user agent."""
    system: str
    """System name for the user agent."""
    browser: str
    """Browser name for the user agent."""
    version: float
    """Version of the browser."""
    os: str
    """OS name for the user agent."""


def load() -> list[BrowserUserAgentData]:
    """Load user agent data from the bundled browsers.json file.

    This function attempts to load user agent data using importlib.resources
    (or importlib_resources for Python < 3.10). If that fails, it falls back
    to pkg_resources. The data file contains one JSON object per line.

    Returns:
        list[BrowserUserAgentData]: List of user agent data dictionaries.
            Each dictionary contains user agent information including the
            user agent string and associated metadata.

    Raises:
        FakeUserAgentError: If the data file cannot be loaded or parsed,
            or if the loaded data is empty or not a list.

    Examples:
        Load user agent data::

            from fake_useragent.utils import load
            data = load()
            print(len(data))  # Number of available user agents
            print(data[0]['useragent'])  # First user agent string
    """
    data = []
    ret: Union[list[BrowserUserAgentData], None] = None
    try:
        json_lines = (
            ilr.files("fake_useragent.data").joinpath("browsers.json").read_text()
        )
        for line in json_lines.splitlines():
            data.append(json.loads(line))
        ret = data
    except Exception as exc:
        # Empty data just to be sure
        data = []
        logger.warning(
            "Unable to find local data/json file or could not parse the contents using importlib-resources. Try pkg-resource next.",
            exc_info=exc,
        )
        try:
            from pkg_resources import resource_filename

            with open(
                resource_filename("fake_useragent", "data/browsers.json")
            ) as file:
                json_lines = file.read()
                for line in json_lines.splitlines():
                    data.append(json.loads(line))
            ret = data
        except Exception as exc2:
            # Empty data just to be sure
            data = []
            logger.warning(
                "Could not find local data/json file or could not parse the contents using pkg-resource.",
                exc_info=exc2,
            )

    if not ret:
        raise FakeUserAgentError("Data list is empty", ret)

    if not isinstance(ret, list):
        raise FakeUserAgentError("Data is not a list ", ret)
    return ret
