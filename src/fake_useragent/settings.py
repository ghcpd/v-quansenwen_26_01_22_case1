"""Configuration settings and constants for the fake_useragent module.

This module defines default settings, string replacements, OS mappings,
and browser shortcuts used throughout the library.
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

