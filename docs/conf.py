from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
INIT_FILE = SRC / "winappaudiorouter" / "__init__.py"


def read_version() -> str:
    content = INIT_FILE.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Cannot find package version.")
    return match.group(1)


sys.path.insert(0, str(SRC))

project = "winappaudiorouter"
author = "winappaudiorouter contributors"
release = read_version()
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_preserve_defaults = True
autodoc_mock_imports = [
    "comtypes",
    "psutil",
    "pycaw",
]

html_theme = "furo"
html_title = f"{project} {release}"
html_show_sourcelink = False
