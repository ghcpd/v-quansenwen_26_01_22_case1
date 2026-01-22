import importlib
import inspect


def _assert_has_doc(obj: object, *, label: str) -> None:
    doc = inspect.getdoc(obj)
    assert doc is not None and doc.strip(), f"Missing docstring: {label}"


def test_api_docs_docstrings_present() -> None:
    """Regression test for API documentation completeness.

    This is intentionally strict: if we remove docstrings from key public modules/classes/methods,
    Sphinx/autodoc output becomes incomplete and this test should fail.
    """

    modules = [
        "fake_useragent",
        "fake_useragent.errors",
        "fake_useragent.fake",
        "fake_useragent.log",
        "fake_useragent.settings",
        "fake_useragent.utils",
    ]

    for mod_name in modules:
        mod = importlib.import_module(mod_name)
        _assert_has_doc(mod, label=f"module {mod_name}")

    from fake_useragent.errors import FakeUserAgentError
    from fake_useragent.fake import FakeUserAgent
    from fake_useragent.utils import BrowserUserAgentData, load

    _assert_has_doc(FakeUserAgentError, label="class FakeUserAgentError")
    _assert_has_doc(FakeUserAgent, label="class FakeUserAgent")
    _assert_has_doc(BrowserUserAgentData, label="type BrowserUserAgentData")
    _assert_has_doc(load, label="function load")

    # Ensure docstrings exist for the most-used user-facing accessors.
    for name in [
        "_filter_useragents",
        "getBrowser",
        "__getitem__",
        "__getattr__",
        "chrome",
        "googlechrome",
        "edge",
        "firefox",
        "ff",
        "safari",
        "random",
        "getFirefox",
        "getChrome",
        "getEdge",
        "getSafari",
        "getRandom",
    ]:
        member = getattr(FakeUserAgent, name)
        _assert_has_doc(member, label=f"FakeUserAgent.{name}")
