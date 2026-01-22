"""Configuration settings and constants for the fake_useragent library.

This module defines version information and various mappings used for normalizing
and translating browser and OS names throughout the library.
"""

from importlib import metadata

__version__ = metadata.version("fake-useragent")

REPLACEMENTS = {
    " ": "",
    "_": "",
}

OS_REPLACEMENTS = {
    "windows": ["win10", "win7"],
}

SHORTCUTS = {
    "microsoft edge": "edge",
    "google": "chrome",
    "googlechrome": "chrome",
    "ff": "firefox",
}
