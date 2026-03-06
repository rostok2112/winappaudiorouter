Installation
============

Requirements
------------

* Windows 10 1803 or newer
* Python 3.10 or newer

Install from PyPI
-----------------

.. code-block:: powershell

   pip install winappaudiorouter

Install for local development
-----------------------------

.. code-block:: powershell

   pip install -e .[dev]

Build the documentation locally
-------------------------------

.. code-block:: powershell

   pip install -r docs/requirements.txt
   pip install -e .
   python -m sphinx -W --keep-going -b html docs docs/_build/html
