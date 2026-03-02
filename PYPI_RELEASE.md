# PyPI Release Instructions

## 1. Prerequisites

1. Create accounts:
   1. https://pypi.org
   2. https://test.pypi.org
2. Install tooling:

```powershell
pip install -e .[dev]
```

## 2. Configure API Tokens

Create `%USERPROFILE%\.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<YOUR_PYPI_TOKEN>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<YOUR_TEST_PYPI_TOKEN>
```

## 3. Build Artifacts

```powershell
python -m build
```

This creates:
- `dist/winappaudiorouter-<version>.tar.gz`
- `dist/winappaudiorouter-<version>-py3-none-any.whl`

## 4. Validate Metadata

```powershell
twine check dist/*
```

## 5. Upload to TestPyPI (recommended)

```powershell
twine upload -r testpypi dist/*
```

Verify install:

```powershell
pip install --index-url https://test.pypi.org/simple/ winappaudiorouter
```

## 6. Upload to PyPI

```powershell
twine upload dist/*
```

## 7. Verify Published Package

```powershell
pip install --upgrade winappaudiorouter
python -c "import winappaudiorouter; print(winappaudiorouter.__version__)"
winappaudiorouter list-devices
```
