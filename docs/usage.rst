Usage
=====

Python API
----------

.. code-block:: python

   import winappaudiorouter as war

   output_devices = war.list_output_devices()
   input_devices = war.list_input_devices()

   output_sessions = war.list_app_sessions()
   input_sessions = war.list_input_sessions()

   war.set_app_output_device(process_name="chrome.exe", device="Headphones")
   war.set_app_input_device(process_name="obs64.exe", device="USB Mic")

   routed_output = war.get_app_output_device(process_name="chrome.exe")
   routed_input = war.get_app_input_device(process_name="obs64.exe")

   war.clear_app_output_device(process_name="chrome.exe")
   war.clear_app_input_device(process_name="obs64.exe")

CLI
---

By default, CLI commands target the output flow. Use ``--flow input`` to work
with capture devices and capture sessions instead.

.. code-block:: powershell

   winappaudiorouter list-devices
   winappaudiorouter list-devices --flow input
   winappaudiorouter list-sessions
   winappaudiorouter list-sessions --flow input
   winappaudiorouter route --process-name chrome.exe --device "Headphones"
   winappaudiorouter route --flow input --process-name obs64.exe --device "USB Mic"
   winappaudiorouter get --process-name chrome.exe
   winappaudiorouter clear --flow input --pid 4567

Operational notes
-----------------

* ``process_name`` routing requires at least one active session for that app in
  the selected flow.
* Session rebinding can be asynchronous. Some apps need playback or recording
  to restart before they pick up the new route.
* Clearing a route removes the persisted override and returns the app to the
  system default device.
