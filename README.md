# minimal_api_docs_project

This is a minimal, executable extraction based on the upstream fix commit `8cfb62ab4b4df13500a21c1d32ae0f95b0641aaf`.

It contains a single regression test that fails if public API docstrings (module/class/method/property) are missing.

## Run

```bash
python -m pip install -e .
python -m pip install pytest
pytest -q
```

## Quick manual sanity

```bash
python -c "from fake_useragent import FakeUserAgent; print(FakeUserAgent().random)"
```
