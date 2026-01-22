"""Configuration and constants for fake_useragent.

Contains replacement rules, OS mappings and shortcuts used by
FakeUserAgent implementation.
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
