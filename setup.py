import re
from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"
INIT_FILE = ROOT / "src" / "winappaudiorouter" / "__init__.py"


def read_version() -> str:
    content = INIT_FILE.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Cannot find __version__ in src/winappaudiorouter/__init__.py")
    return match.group(1)


setup(
    name="winappaudiorouter",
    version=read_version(),
    description="Route Windows app audio output and input devices using the same policy API path as EarTrumpet.",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="winappaudiorouter contributors",
    url="https://github.com/rostok2112/winappaudiorouter",
    project_urls={
        "Homepage": "https://github.com/rostok2112/winappaudiorouter",
        "Repository": "https://github.com/rostok2112/winappaudiorouter",
        "Issues": "https://github.com/rostok2112/winappaudiorouter/issues",
    },
    license="MIT",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "comtypes>=1.4.6",
        "psutil>=5.9",
        "pycaw>=20240210",
    ],
    extras_require={
        "dev": [
            "build>=1.2.2",
            "pytest>=8.3",
            "twine>=6.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "winappaudiorouter=winappaudiorouter.cli:main",
        ],
    },
    keywords=["windows", "audio", "routing", "input", "output", "pycaw", "eartrumpet"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
