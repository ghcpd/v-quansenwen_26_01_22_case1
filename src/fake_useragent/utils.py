"""Utility functions and types for the fake_useragent module.

This module provides data loading functions and type definitions for
user agent data structures.
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
    """A dictionary containing user agent information for a specific browser configuration.
    
    Attributes:
        useragent (str): The user agent string.
        percent (float): Sampling probability for this user agent when random sampling. 
            Currently has no effect.
        type (str): The device type for this user agent (e.g., 'pc', 'mobile', 'tablet').
        system (str): System name for the user agent (e.g., 'Chrome 122.0 Win10').
        browser (str): Browser name for the user agent (e.g., 'chrome', 'firefox', 'safari', 'edge').
        version (float): Version number of the browser.
        os (str): Operating system name for the user agent (e.g., 'win10', 'macos', 'linux').
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


# Load all lines from browser.json file
# Returns array of objects
def load() -> list[BrowserUserAgentData]:
    """Load user agent data from the local browsers.json data file.
    
    This function loads browser user agent data from a bundled JSON file,
    falling back to pkg_resources if importlib.resources is unavailable.
    
    Returns:
        list[BrowserUserAgentData]: A list of user agent data dictionaries,
            each containing information about a specific browser configuration.
    
    Raises:
        FakeUserAgentError: If the data file cannot be found, parsed, or is invalid
            (empty list or not a list type).
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

