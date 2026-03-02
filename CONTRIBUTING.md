# Contributing to winappaudiorouter

Thanks for contributing.

## Development setup

1. Create a virtual environment and activate it.
2. Install dependencies:

```powershell
pip install -e .[dev]
```

## Local checks

```powershell
python -m pytest -q
python -m build
python -m twine check dist/*
```

## Pull requests

1. Create a feature branch from `main`.
2. Add or update tests for behavior changes.
3. Keep commits focused and descriptive.
4. Ensure CI is green before requesting review.