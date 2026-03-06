winappaudiorouter
=================

``winappaudiorouter`` is a Python library for routing Windows app audio to
specific output and input devices through the same Windows policy API path used
by tools such as EarTrumpet.

The library exposes both a Python API and a CLI for:

* Listing active output and input devices
* Listing active audio sessions by flow
* Routing an app to a chosen output or input device
* Clearing a per-app route back to the system default device
* Querying the currently persisted per-app route

.. note::

   ``winappaudiorouter`` is Windows-only. The documentation is built on Linux,
   so Windows-specific dependencies are mocked during the doc build.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   api
